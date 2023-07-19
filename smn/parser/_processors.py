"""API processors which used in web parsers."""
from typing import Union

try:
    import orjson as json
except ImportError:
    import json  # type: ignore
from httpx import Response


class NoFileProvidedError(ValueError):
    pass


def simple(r: Union[Response, str, dict], fields: Union[tuple, list, str], *_):
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
                f"[{r.status_code}] {r.content!r}" if isinstance(r, Response) else r
            )
    return file
