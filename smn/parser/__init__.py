"""
The place where all parsers must be defined.

TgParserTemplate:
    — link to the channel
    — channel_id — provide only if link belongs to a private channel,
                   otherwise it will be ignored
    — adfilter — enable/disable ad filtering
    — allowed_links — links ignored by adfilter

WebParserTemplate:
    — link to the web api
    — process — coroutine defined at _processors.py.
                parser calls it using Response, args, kwargs as three arguments.
    — *args
    — method — http method which will be used to fetch the api
    — headers
    — timeout
    — ignore_status_code
    — **kwargs

To configure probabilities change the WEIGHTS variable.
Example:
    PARSERS = (A, B, C, D, F)
    WEIGHTS = (1, 2, 1, 3, 3)
    A - 10%, B - 20%, C - 10%, D - 30%, F - 30%
"""

from .base import TgParserTemplate, WebParserTemplate
from ._processors import simple
from ..config import HELPER_ENABLED


PARSERS = (
    WebParserTemplate("https://nekos.life/api/neko", simple, "neko"),
    WebParserTemplate("https://aws.random.cat/meow", simple, "file"),
    WebParserTemplate("https://nekos.best/api/v2/neko", simple, "results", "url"),
    WebParserTemplate("http://api.nekos.fun:8080/api/neko", simple, "image"),
    WebParserTemplate("https://api.waifu.pics/sfw/neko", simple, "url"),
    *(
        (
            TgParserTemplate("cats_cats", adfilter=False),
            TgParserTemplate("pishistyieinvalidii"),
            TgParserTemplate("kisyy"),
            TgParserTemplate(
                "https://t.me/+773vT3a93nQ2Mzc6", channel_id=-1001215035444
            ),
        )
        if HELPER_ENABLED
        else ()
    ),
)

# Weight - probability of parser selection
# PARSERS[i] has weight WEIGHTS[i]
WEIGHTS = None

### Do not edit! ###

import logging

from .base import UserCli
from .types import Parsers

if WEIGHTS is not None and len(PARSERS) != len(WEIGHTS):
    logging.error("Lengths of parsers & weights are not equal.")
    WEIGHTS = None

PARSERS = Parsers(PARSERS, WEIGHTS)

__all__ = ("base", "UserCli", "PARSERS")
