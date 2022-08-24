from typing import Union, Iterable, Tuple
from telethon.tl.types import TypeMessage


def format_ids(messages: Union[Iterable[TypeMessage], TypeMessage]):
    if isinstance(messages, Iterable):
        return ", ".join([str(m.id) for m in messages])
    return str(messages.id)


async def retry_on_exc(
    coro,
    *args,
    retries: int = 3,
    exceptions: Union[Tuple[BaseException], BaseException] = Exception,
    **kwargs,
):
    counter = 0
    while counter < retries:
        counter += 1
        try:
            return await coro(*args, **kwargs)
        except exceptions:
            continue
    raise Exception
