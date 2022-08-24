import logging
import asyncio
import sys

try:
    import coloredlogs
except (ImportError, ModuleNotFoundError):
    _formatter = logging.Formatter
else:
    _formatter = coloredlogs.ColoredFormatter

from .config import LOG_CHAT


class TgHandler(logging.Handler):
    def __init__(self, client: "TelegramClient", target: int = LOG_CHAT):
        super().__init__(0)
        self.client = client
        self.target = target

    def emit(self, record):
        msg = _tg_formatter.format(record)
        # FIXME: perhaps i should do something with that...
        asyncio.ensure_future(self.client.send_message(self.target, msg))


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

    tghandler = TgHandler(cli)
    tghandler.setLevel(lvl)

    logging.getLogger().handlers = []
    logging.getLogger().addHandler(handler)
    logging.getLogger().addHandler(TgHandler(cli))
    logging.getLogger().setLevel(lvl)
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logging.getLogger("hpack").setLevel(logging.WARNING)
    logging.captureWarnings(True)
