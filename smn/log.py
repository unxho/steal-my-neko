import asyncio
import logging
import sys

try:
    _formatter: type[logging.Formatter]
    import coloredlogs
except ImportError:
    _formatter = logging.Formatter
else:
    _formatter = coloredlogs.ColoredFormatter

from telethon.errors import FloodWaitError

from .config import LOG_CHAT


class TgHandler(logging.Handler):
    def __init__(
        self,
        client: "TelegramClient",  # type: ignore # noqa
        target: int = LOG_CHAT,
        delay: int = 1,
    ):
        super().__init__(0)
        self.client = client
        self.target = target
        self.delay = delay
        self.queue = []
        self.lck = False

    def emit(self, record):
        msg = _tg_formatter.format(record)
        self.queue.append(msg)
        if not self.lck:
            asyncio.ensure_future(self.watcher())

    async def watcher(self):
        self.lck = True
        while self.queue:
            msg = self.queue[0]
            del self.queue[0]
            try:
                await self.client.send_message(self.target, msg)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            else:
                await asyncio.sleep(self.delay)
        self.lck = False


_main_formatter = _formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    style="%",
)

_tg_formatter = logging.Formatter(
    fmt="`[%(levelname)s] %(name)s: %(message)s`",
    datefmt=None,
    style="%",
)


def init(cli):
    lvl = logging.DEBUG if "--debug" in sys.argv else logging.INFO

    handler = logging.StreamHandler()
    handler.setLevel(lvl)
    handler.setFormatter(_main_formatter)

    logging.getLogger().handlers = []
    logging.getLogger().addHandler(handler)
    logging.getLogger().addHandler(TgHandler(cli))
    logging.getLogger().setLevel(lvl)

    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("hpack").setLevel(logging.WARNING)
    logging.captureWarnings(True)
