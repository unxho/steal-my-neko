__all__ = ['base', 'UserCli', 'PARSERS']

from .base import WebParserTemplate, TgParserTemplate, UserCli
from ._processors import nekoslife, randomcat, nekosbest, nekosfun

NekosLifeParser = WebParserTemplate('https://nekos.life/api/neko', nekoslife)
RandomCatParser = WebParserTemplate('https://aws.random.cat/meow', randomcat)
NekosBestParser = WebParserTemplate('https://nekos.best/api/v2/neko',
                                    nekosbest)
NekosFunParser = WebParserTemplate('http://api.nekos.fun:8080/api/neko',
                                   nekosfun)

CatsCatsParser = TgParserTemplate('cats_cats', adfilter=False)
NekoArchiveEroParser = TgParserTemplate('Neko_Girls_Ero')
PishistyeInvalidiParser = TgParserTemplate('pishistyieinvalidi')

PARSERS = (NekosLifeParser, RandomCatParser, NekosBestParser, CatsCatsParser,
           NekoArchiveEroParser, PishistyeInvalidiParser, NekosFunParser)
