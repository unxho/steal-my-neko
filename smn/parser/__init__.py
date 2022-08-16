__all__ = ["base", "UserCli", "PARSERS"]

from .base import WebParserTemplate, TgParserTemplate, UserCli
from ._processors import nekoslife, randomcat, nekosbest, nekosfun, waifupics

NekosLifeParser = WebParserTemplate("https://nekos.life/api/neko", nekoslife)
RandomCatParser = WebParserTemplate("https://aws.random.cat/meow", randomcat)
NekosBestParser = WebParserTemplate("https://nekos.best/api/v2/neko", nekosbest)
NekosFunParser = WebParserTemplate("http://api.nekos.fun:8080/api/neko", nekosfun)
WaifuPicsParser = WebParserTemplate("https://api.waifu.pics/sfw/neko", waifupics)

CatsCatsParser = TgParserTemplate("cats_cats", adfilter=False)
NekoArchiveEroParser = TgParserTemplate(
    "https://t.me/+SYOwjbbXYsY0NzM6", channel_id=-1001215035444
)
PishistyeInvalidiParser = TgParserTemplate("pishistyieinvalidii")
KisyyParser = TgParserTemplate("kisyy")

PARSERS = (
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
