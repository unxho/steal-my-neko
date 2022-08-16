"""API processors which used in web parsers."""
try:
    import orjson as json
except (ImportError, ModuleNotFoundError):
    import json
from httpx import Response


class NoFileProvidedError(ValueError):
    pass


def simple(r: Response or str or dict, fields: tuple or list or str):
    """Gets the file url from some specific json field."""
    if isinstance(fields, str):
        fields = [fields]
    if isinstance(r, Response):
        file = json.loads(r.content)
    elif isinstance(r, str):
        file = json.loads(r)
    else:
        file = r
    for field in fields:
        if isinstance(file, (list, tuple)):
            file = file[0]
        file = file.get(field)
        if not file:
            raise NoFileProvidedError(
                f"[{r.status_code}] {r.content}" if isinstance(r, Response) else r
            )
    return file


async def nekoslife(r: Response, *_):
    """nekos.life processor"""
    return simple(r, "neko")


async def randomcat(r: Response, *_):
    """aws.random.cat processor"""
    return simple(r, "file")


async def nekosbest(r: Response, *_):
    """nekos.best processsor"""
    return simple(r, ("results", "url"))


async def nekosfun(r: Response, *_):
    """nekos.fun processor"""
    return simple(r, "image")


async def waifupics(r: Response, *_):
    """waifu.pics processor"""
    return simple(r, "url")
