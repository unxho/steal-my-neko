from typing import Coroutine
from random import randint
from httpx import AsyncClient as HttpClient, codes, Request,\
                  ConnectTimeout, ConnectError
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from .. import config, utils

UserCli = Client('.nekohelper',
                 config.API_ID,
                 config.API_HASH,
                 phone_number=config.HELPER_PHONE)\
          if config.HELPER_ENABLED else None


class TgParserTemplate:

    def __init__(self,
                 link: str,
                 *,
                 client: Client = None,
                 adfilter: bool = True):

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
        if not link.startswith(('http:', 'https:')):
            if not link.startswith('@'):
                link = '@' + link
        self.link = link
        self.adf = adfilter
        self.chat = self._client.join_chat(link)
        self._cache = []
        self._client.add_handler(
            MessageHandler(
                self._cache_update,
                filters.chat(self.chat.id)
                & (filters.photo | filters.video | filters.animation)
                & filters.create(self.adfilter_stub)))

    async def _cache_everything(self):
        clean_cache = []
        async for m in self._client.get_chat_history(self.link, 50):
            if self.adfilter(m):
                clean_cache.append(m.id)
        self._cache = clean_cache

    async def _cache_update(self, _, m):
        self._cache.append(m.id)

    def adfilter_stub(self, _, m: Message):
        return self.adfilter(m)

    def adfilter(self, m: Message):
        if not utils.get_media(m):
            return False
        if self.adf and (m.media_group_id or m.forward_from):
            # ignoring albums because it most likely an ad
            return False
        if m.empty or (not m.text and not m.caption):
            return True
        if self.adf:
            text = m.text if m.text else m.caption
            text = text.markdown.replace(self.link, '')
            if self.link.startswith('http:'):
                text = text.replace('https' + self.link[4:], '')
            elif self.link.startswith('https:'):
                text = text.replace('http' + self.link[5:], '')
            if 'http' in text:
                return False
            if '@' in text:
                for i in text.split():
                    if i.startswith('@') and i.count('@') == 1 and len(i) != 1:
                        return False
        return True

    async def recv(self):
        if not self._client:
            raise ReceiveError("Helper disabled.")
        if not self._cache:
            await self._cache_everything()
            if not self._cache:
                raise ReceiveError(
                    f"Parser {self.link} seems unable to cache.")
        media_ind = randint(0, len(self._cache) - 1)
        media = self._cache[media_ind]
        del self._cache[media_ind]
        return media


class WebParserTemplate:

    def __init__(self,
                 url: str,
                 process: Coroutine,
                 method: str = 'GET',
                 headers: dict = {},
                 timeout: float or int = 10,
                 ignore_status_code: bool = False,
                 *args,
                 **kwargs):

        self._session = HttpClient(headers=headers, timeout=timeout)
        self.process = process
        self.url, self.method = url, method
        self.ignore_status_code = ignore_status_code
        self.args, self.kwargs = args, kwargs

    async def recv(self):

        request = Request(self.method, self.url)
        counter = 0
        while counter < 3:
            counter += 1
            try:
                response = await self._session.send(request)
                if not self.ignore_status_code\
                   and response.status_code != codes.OK:
                    continue
                break
            except (ConnectError, ConnectTimeout):
                continue
        else:
            raise ReceiveError(f"Connection to {self.url} failed 3 times.")

        return await self.process(response, self.args, self.kwargs)


class ReceiveError(ConnectError):
    pass
