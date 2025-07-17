from collections.abc import Awaitable, Iterable
from typing import Any, Callable

from telethon.tl.types import Message


def format_ids(messages: Iterable[Message] | Message) -> str:
    if isinstance(messages, Iterable):
        return ", ".join([str(m.id) for m in messages])
    return str(messages.id)


async def retry_on_exc(
    coro: Callable[[Any, Any], Awaitable[Any]],
    *args,
    retries: int = 3,
    exceptions=Exception,
    **kwargs,
) -> Any:
    counter = 0
    while counter < retries:
        counter += 1
        try:
            return await coro(*args, **kwargs)
        except exceptions:
            continue
    raise Exception


def search(lst: Iterable[Any], func: Callable[..., bool]) -> int | None:
    for i, v in enumerate(lst):
        if func(v):
            return i
    return None
