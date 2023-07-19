"""
The place where all parsers must be defined.

TgParserTemplate:
    — link to the channel
    — channel_id – provide only if link belongs to a private channel,
                   otherwise it will be ignored
    – adfilter – enable/disable ad filtering

WebParserTemplate:
    — link to the web api
    — process — coroutine defined at _processors.py.
                parser calls it using Response, args, kwargs as three arguments.
    – *args
    — method — http method which will be used to fetch the api
    – headers
    – timeout
    – ignore_status_code
    – **kwargs
"""

__all__ = ["base", "UserCli", "PARSERS"]

from ._processors import simple
from .base import TgParserTemplate, UserCli, WebParserTemplate

NekosLifeParser = WebParserTemplate("https://nekos.life/api/neko", simple, "neko")
RandomCatParser = WebParserTemplate("https://aws.random.cat/meow", simple, "file")
NekosBestParser = WebParserTemplate(
    "https://nekos.best/api/v2/neko", simple, "results", "url"
)
NekosFunParser = WebParserTemplate(
    "http://api.nekos.fun:8080/api/neko", simple, "image"
)
WaifuPicsParser = WebParserTemplate(
    "https://api.waifu.pics/sfw/neko", simple, "url"
)

CatsCatsParser = TgParserTemplate("cats_cats", adfilter=False)
NekoArchiveEroParser = TgParserTemplate(
    "https://t.me/+773vT3a93nQ2Mzc6", channel_id=-1001215035444
)
PishistyeInvalidiParser = TgParserTemplate("pishistyieinvalidii")
KisyyParser = TgParserTemplate("kisyy")

PARSERS = (
    # *(NekoArchiveEroParser,)*3  <-- multiply to increase probability
    NekosLifeParser,
    RandomCatParser,
    NekosBestParser,
    CatsCatsParser,
    NekoArchiveEroParser,
    PishistyeInvalidiParser,
    NekosFunParser,
    WaifuPicsParser,
    KisyyParser,
)
