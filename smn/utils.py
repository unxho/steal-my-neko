from typing import Any, Callable, Iterable, Tuple, Union

from telethon.tl.types import TypeMessage


def format_ids(messages: Union[Iterable[TypeMessage], TypeMessage]) -> str:
    if isinstance(messages, Iterable):
        return ", ".join([str(m.id) for m in messages])
    return str(messages.id)


async def retry_on_exc(
    coro,
    *args,
    retries: int = 3,
    exceptions: Union[Tuple[BaseException], BaseException] = Exception,
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


def search(lst: Iterable, func: Callable) -> Union[int, None]:
    for i, v in enumerate(lst):
        if func(v):
            return i
