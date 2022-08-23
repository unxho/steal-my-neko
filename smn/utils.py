def format_ids(messages):
    if isinstance(messages, list):
        return ", ".join([str(m.id) for m in messages])
    return str(messages.id)


async def retry_on_exc(
    coro, *args, retries: int = 3, exceptions: tuple = (Exception), **kwargs
):
    counter = 0
    while counter < retries:
        counter += 1
        try:
            return await coro(*args, **kwargs)
        except exceptions:
            continue
    raise Exception
