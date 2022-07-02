"""API processors which used in web parsers."""
try:
    import orjson as json
except (ImportError, ModuleNotFoundError):
    import json
from httpx import Response


class NoFileProvidedError(ValueError):
    pass


def simple(r: Response, field):
    """Gets the file url from some specific json field."""
    file = json.loads(r.content).get(field)
    if not file:
        raise NoFileProvidedError(f'[{r.status_code}] {r.content}')
    return file


async def nekoslife(r: Response, *_):
    """nekos.life processor"""
    return simple(r, 'neko')


async def randomcat(r: Response, *_):
    """aws.random.cat processor"""
    return simple(r, 'file')


async def nekosbest(r: Response, *_):
    """nekos.best processsor"""
    d = simple(r, 'results')[0].get('url')
    if not d:
        raise NoFileProvidedError(f'[{r.status_code}] {r.content}')
    return d

async def nekosfun(r: Response, *_):
    """nekos.fun processor"""
    return simple(r, 'image')
