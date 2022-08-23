import asyncio
import logging
from typing import Coroutine
from random import randint
from httpx import (
    AsyncClient as HttpClient,
    codes,
    Request,
    ConnectTimeout,
    ConnectError,
)
from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.tl.types import MessageEntityTextUrl
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors.rpcerrorlist import UserAlreadyParticipantError

try:
    from tqdm.asyncio import tqdm
except ImportError:

    def tqdm(*args, **kwargs):
        if args:
            return args[0]
        return kwargs.get("iterable", None)


from .types import VerifiedList
from .. import config, utils

UserCli = (
    TelegramClient(".nekohelper", config.API_ID, config.API_HASH)
    if config.HELPER_ENABLED
    else None
)
loop = asyncio.get_event_loop()
logger = logging.getLogger("parser")


class TgParserTemplate:
    def __init__(
        self,
        link: str,
        *,
        client: TelegramClient = None,
        adfilter: bool = True,
        channel_id=None,
    ):

        if not client:
            self._client = UserCli
        else:
            self._client = client
        if not self._client:
            return
        try:
            self._client.start()
        except ConnectionError:
            pass

        if not link.startswith(("http:", "https:")):
            if not link.startswith("@"):
                link = "@" + link
            self.chat = loop.run_until_complete(self._client(JoinChannelRequest(link)))
        else:
            try:
                self.chat = loop.run_until_complete(
                    self._client(ImportChatInviteRequest(link.split("+", 1)[1]))
                )
            except UserAlreadyParticipantError:
                if not channel_id:
                    raise Exception(
                        "We can't work only with invite links."
                        "Please, provide the channel_id."
                    )
                self.chat = loop.run_until_complete(self._client.get_entity(channel_id))
        if hasattr(self.chat, "chats"):
            self.chat = self.chat.chats[0]

        self.link = link
        self.adf = adfilter
        self._cache = []
        self._client.add_event_handler(
            self._cache_update,
            NewMessage(incoming=True, from_users=self.chat),
        )
        self._known_albums = {}

    async def _cache_everything(self):
        clean_cache = []
        _album_queue = {}
        limit = 50
        counter = 0
        latest_msg_is_part_of_album = False

        messages = tqdm(
            self._client.iter_messages(self.chat),
            total=limit,
            desc="Caching",
            leave=False,
            colour="green",
        ).__enter__()

        async for m in messages:
            m.verified = False
            if m.grouped_id:
                if not _album_queue.get(m.grouped_id):
                    _album_queue[m.grouped_id] = VerifiedList()
                _album_queue[m.grouped_id].append(m)
                latest_msg_is_part_of_album = True
                # force continuing loop without limit checks
                continue
            # album is fully handled now
            if latest_msg_is_part_of_album:
                counter += 1
                latest_msg_is_part_of_album = False
            counter += 1

            if self.adfilter(m):
                m.verified = True
                clean_cache.append(m)

            if counter > limit:
                break

        messages.close()

        for album in _album_queue.values():
            boo = False
            for i, m in enumerate(album):
                if not self.adfilter(m):
                    boo = True
                    break
                album[i].verified = True
            if boo:
                continue
            clean_cache.append(album)

        self._cache = clean_cache

    async def _cache_update(self, m):
        m.verified = self.adfilter(m)
        if m.grouped_id:
            if not self._known_albums.get(m.grouped_id):
                self._known_albums[m.grouped_id] = VerifiedList()
            self._known_albums[m.grouped_id].append(m)
            self._cache.append(m)
            return
        if m.verified:
            self._cache.append(m)

    def adfilter(self, m):

        if hasattr(m, "messages"):
            for m_ in m.messages:
                if not self.adfilter(m_):
                    return False
            return True

        if (
            not m.media
            or m.sticker
            or (self.adf and (m.fwd_from or m.buttons))
            # ignoring fwds/buttons because it most likely an ad
        ):
            return False

        if not m.text:
            return True

        if self.adf:
            text = m.text.replace(self.link, "")
            if self.link.startswith("http:"):
                text = text.replace("https" + self.link[4:], "")
            elif self.link.startswith("https:"):
                text = text.replace("http" + self.link[5:], "")
            if "http" in text:
                return False
            if "@" in text:
                for i in text.split():
                    if i.startswith("@") and i.count("@") == 1 and len(i) != 1:
                        return False
            # received text does not contain ads,
            # checking hidden message entities...
            if m.entities:
                for e in m.entities:
                    if isinstance(e, MessageEntityTextUrl):
                        if e.url != self.link:
                            return False

        return True

    async def recv(self):

        if not self._client:
            raise ReceiveError("Helper disabled.")
        if not self._cache:
            await self._cache_everything()
            if not self._cache:
                raise ReceiveError(f"Parser {self.link} seems unable to cache.")

        media_ind = randint(0, len(self._cache) - 1)
        media = self._cache[media_ind]
        del self._cache[media_ind]

        if not isinstance(media, list) and media.grouped_id in self._known_albums:
            media = self._known_albums.pop(media.grouped_id)
            for i, m in enumerate(self._cache):
                if isinstance(m, list):
                    m = m[0]
                if m.grouped_id == media[0].grouped_id:
                    del self._cache[i]
            # we need to check the whole group again

        elif isinstance(media, list):
            media.reverse()

        if not media.verified:
            if logger.isEnabledFor(logging.DEBUG):
                logging.debug(
                    "Media not verified: "
                    + self.link
                    + " -> "
                    + utils.format_ids(media)
                )
            return await self.recv()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(self.link + " -> " + utils.format_ids(media))

        return media


class WebParserTemplate:
    def __init__(
        self,
        url: str,
        process: Coroutine,
        method: str = "GET",
        headers: dict = {},
        timeout: float or int = 10,
        ignore_status_code: bool = False,
        *args,
        **kwargs,
    ):

        self._session = HttpClient(headers=headers, timeout=timeout, http2=True)
        self.process = process
        self.url, self.method = url, method
        self.ignore_status_code = ignore_status_code
        self.args, self.kwargs = args, kwargs

    async def recv(self):

        request = Request(self.method, self.url)
        try:
            response = await utils.retry_on_exc(
                self._session.send, request, exceptions=(ConnectError, ConnectTimeout)
            )
        except Exception:
            raise ReceiveError
        if not self.ignore_status_code and response.status_code != codes.OK:
            raise ReceiveError

        return await self.process(response, self.args, self.kwargs)


class ReceiveError(ConnectError):
    pass
