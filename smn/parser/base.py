import asyncio
import logging
from random import randint
from typing import Callable, List, Optional, Union

from httpx import AsyncClient as HttpClient
from httpx import ConnectError, ConnectTimeout, Request, codes
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import (
    ChannelPrivateError,
    InviteRequestSentError,
    UserAlreadyParticipantError,
)
from telethon.events import NewMessage
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import (
    MessageEntityTextUrl,
    MessageMediaContact,
    MessageMediaDice,
    MessageMediaEmpty,
    MessageMediaGame,
    MessageMediaGeo,
    MessageMediaGeoLive,
    MessageMediaInvoice,
    MessageMediaPoll,
    MessageMediaUnsupported,
    MessageMediaVenue,
    MessageMediaWebPage,
    TypeMessage,
)

try:
    from tqdm.asyncio import tqdm
except ImportError:

    def tqdm(*args, **kwargs):
        if args:
            return args[0]
        return kwargs.get("iterable", None)


from .. import config, utils
from .types import VerifiedList

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
        client: Optional[TelegramClient] = None,
        adfilter: bool = True,
        channel_id: Optional[int] = None,
        allowed_links: List[str] = [],
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
            self.chat = loop.run_until_complete(
                self._client(JoinChannelRequest(link))
            )
        else:
            try:
                self.chat = loop.run_until_complete(
                    self._client(
                        ImportChatInviteRequest(link.split("+", 1)[1])
                    )
                )
            except UserAlreadyParticipantError:
                if not channel_id:
                    raise Exception(
                        "We can't work only with invite links."
                        "Please, provide the channel_id."
                    )
                self.chat = loop.run_until_complete(
                    self._client.get_entity(channel_id)
                )
            except InviteRequestSentError:
                loop.run_until_complete(asyncio.sleep(1))
                while True:
                    try:
                        self.chat = loop.run_until_complete(
                            self._client.get_entity(channel_id)
                        )
                        break
                    except (ChannelPrivateError, ValueError):
                        # lets wait...
                        loop.run_until_complete(asyncio.sleep(10))

        if hasattr(self.chat, "chats"):
            self.chat = self.chat.chats[0]

        self.link = link
        self.adf = adfilter
        self.allowed_links = allowed_links
        self._cache = []
        self._client.add_event_handler(
            self._cache_update,
            NewMessage(incoming=True, from_users=self.chat),
        )

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

    async def _cache_update(self, m: TypeMessage):
        m.verified = self.adfilter(m)
        if m.grouped_id:
            i = utils.search(
                self._cache,
                lambda i: i[0].grouped_id == m.grouped_id
                if isinstance(i, list)
                else False,
            )
            if i == None:  # noqa
                self._cache.append(VerifiedList())
                i = len(self._cache) - 1  # -1 seems insecure
                self._cache[i].must_not_be_reversed = True
            self._cache[i].append(m)
            return

        if m.verified:
            self._cache.append(m)

    def adfilter(self, m: TypeMessage) -> bool:

        if hasattr(m, "messages"):
            for m_ in m.messages:
                if not self.adfilter(m_):
                    return False
            return True

        if (
            not m.media
            or m.sticker
            or isinstance(
                m.media,
                (
                    MessageMediaWebPage,
                    MessageMediaVenue,
                    MessageMediaGeoLive,
                    MessageMediaInvoice,
                    MessageMediaContact,
                    MessageMediaGame,
                    MessageMediaEmpty,
                    MessageMediaDice,
                    MessageMediaGeo,
                    MessageMediaPoll,
                    MessageMediaUnsupported,
                ),
            )
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
            for link in self.allowed_links:
                text = text.replace(link, "")
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
                        if e.url not in [self.link] + self.allowed_links:
                            return False

        return True

    async def recv(self):

        if not self._client:
            raise ReceiveError("Helper disabled.")
        if not self._cache:
            await self._cache_everything()
            if not self._cache:
                raise ReceiveError(
                    f"Parser {self.link} seems unable to cache."
                )

        media_ind = randint(0, len(self._cache) - 1)
        media = self._cache[media_ind]
        del self._cache[media_ind]

        if not media.verified:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(
                    "Media not verified: "
                    + self.link
                    + " -> "
                    + utils.format_ids(media)
                )
            return await self.recv()

        if isinstance(media, list):

            if (
                hasattr(media, "must_not_be_reversed")
                and media.must_not_be_reversed
            ):
                pass
            else:
                media.reverse()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(self.link + " -> " + utils.format_ids(media))

        return media


class WebParserTemplate:
    def __init__(
        self,
        url: str,
        process: Callable,
        *args,
        method: str = "GET",
        headers: dict = {},
        timeout: Union[float, int] = 10,
        ignore_status_code: bool = False,
        **kwargs,
    ):

        self._session = HttpClient(
            headers=headers, timeout=timeout, http2=True
        )
        self.process = process
        self.url, self.method = url, method
        self.ignore_status_code = ignore_status_code
        self.args, self.kwargs = args, kwargs

    async def recv(self):

        try:
            response = await utils.retry_on_exc(
                self._session.send,
                Request(self.method, self.url),
                exceptions=(ConnectError, ConnectTimeout),
            )
        except Exception:
            raise ReceiveError

        if not self.ignore_status_code and response.status_code != codes.OK:
            raise ReceiveError
        if asyncio.iscoroutinefunction(self.process):
            return await self.process(response, self.args, self.kwargs)
        else:
            return self.process(response, self.args, self.kwargs)


class ReceiveError(ConnectError):
    pass
