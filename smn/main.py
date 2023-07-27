import asyncio
import logging
import sys
from collections.abc import Iterable
from datetime import datetime
from random import choice, choices, randint
from signal import SIGINT
from typing import NoReturn, Optional, Union

from telethon import TelegramClient
from telethon.errors import BadRequestError, FileReferenceExpiredError
from telethon.events import NewMessage
from telethon.tl.types import TypeChat, TypeMessageMedia

from . import config, log
from .dubctl import DubsDataFile
from .parser.base import Parser, ReceiveError

client = TelegramClient(".nekoposter", config.API_ID, config.API_HASH)
client.start(bot_token=config.BOT_TOKEN)
log.init(client)

from .parser import PARSERS, UserCli

channel = config.CHANNEL
log_chat = config.LOG_CHAT
dublicates = DubsDataFile()

loop = asyncio.get_event_loop()
loop.run_until_complete(dublicates._post_init())
SUSPENDED = False
FIRST_RUN = True


async def post(
    file: Union[list[TypeMessageMedia], str],
    test: bool = "--test" in sys.argv,
    ids: Optional[Iterable[int]] = None,
    entity: Optional[TypeChat] = None,
):
    out = channel if not test else log_chat
    try:
        if isinstance(file, str) and file.startswith(("http:", "https:")):
            await client.send_message(out, config.CAPTION, file=file)
        else:
            if isinstance(file, list) and len(file) == 1:
                file = file[0]
            await UserCli.send_message(out, config.CAPTION, file=file)
        return
    except BadRequestError as e:
        if (
            not isinstance(e, FileReferenceExpiredError)
            and "FILE_REFERENCE_0_EXPIRED" not in e.message
        ):
            logging.debug(e)
            raise ReceiveError(str(file) + " is too big or unreachable.") from e

        logging.debug("File reference expired, refetching messages...")
        file = []
        # refetching outdated media objects
        async for m in UserCli.iter_messages(entity, ids=ids):
            if not m:
                raise ReceiveError("Message does not exist.") from e
            file.append(m.media)
        await post(file, test, ids, entity)


async def wait():
    global FIRST_RUN
    if FIRST_RUN and config.WAIT_UNTIL_NEW_HOUR:
        seconds = (60 - datetime.now().minute) * 60
    elif config.FREQUENCY_AS_RANGE and len(config.FREQUENCY) == 2:
        seconds = randint(*config.FREQUENCY)
    else:
        seconds = choice(config.FREQUENCY)

    logging.debug("Waiting: %s", str(seconds))
    await asyncio.sleep(seconds)


async def receiver(parser: Parser):
    """
    Main parse wrapper.

    Message/list - list of messages
    str          - link to file
    bytes        - file data
    """
    if config.FALLBACK:
        async for latest_msg in UserCli.iter_messages(config.CHANNEL, 1):
            if (datetime.now() - latest_msg.date).seconds < config.FALLBACK_TIMEOUT:
                return None
    try:
        file = await parser.recv()
    except ReceiveError as e:
        logging.debug(e)
        parsers = PARSERS
        parsers.remove(parser)
        if not parsers:
            parsers = PARSERS  # type: ignore
        return await receiver(choices(parsers, parsers.weights)[0])

    dub_candidate = ""
    if not isinstance(file, (str, bytes, list)):
        # Message
        file = [file]

    msg_ids = []
    entity = None
    if isinstance(file, list):
        # Messages
        file_ = file
        file = []
        entity = parser.chat  # type: ignore
        for f in file_:
            dub_candidate = str(parser.chat.id) + ":" + str(f.id)  # type: ignore
            if dub_candidate in dublicates.data or not f.media:
                logging.debug("Dublicate: %s", dub_candidate)
                return await receiver(choices(PARSERS, PARSERS.weights)[0])
            msg_ids.append(f.id)
            file.append(f.media)

    elif isinstance(file, str):
        # Link
        dub_candidate = file.split("/")[-1]
        if dub_candidate in dublicates.data:
            logging.debug("Dublicate: %s", dub_candidate)
            return await receiver(choice(PARSERS))
    # elif isinstance(file, bytes):
    # TODO: raw data does not support dublicate checks
    if dub_candidate:
        await dublicates.update(dub_candidate)
    try:
        return await post(file, ids=msg_ids, entity=entity)
    except ReceiveError:
        return await receiver(choices(PARSERS, PARSERS.weights)[0])


async def worker() -> NoReturn:
    logging.info("Launched.")
    global FIRST_RUN
    while True:
        if SUSPENDED:
            await wait()
            continue
        if FIRST_RUN and not config.POST_ON_FIRST_RUN:
            await wait()
        try:
            await receiver(choices(PARSERS, PARSERS.weights)[0])
        except BaseException as e:
            logging.exception(e)
        FIRST_RUN = False
        await wait()


async def stdin_handler() -> NoReturn:
    print(
        "Hello!\nSteal My Neko control commands:\n"
        "- post - to force a post\n"
        "- suspend - to (un)suspend posting\n"
        "- exit - to finish this program.\n\n"
    )
    while True:
        msg = (await loop.run_in_executor(None, input)).lower()
        if msg == "post":
            try:
                await receiver(choices(PARSERS, PARSERS.weights)[0])
                print("Success!")
            except BaseException as e:
                logging.exception(e)
                print("Failed.")
        elif msg == "suspend":
            global SUSPENDED
            SUSPENDED = not SUSPENDED
            print("Done! Status:", SUSPENDED)
        elif msg == "exit":
            print("Bye-bye.")
            sys.exit(0)


if config.ADMIN:

    @client.on(
        NewMessage(
            from_users=config.ADMIN,
            incoming=True,
            func=lambda m: m.raw_text,
        )
    )
    async def bot_handler(event):
        if event.raw_text.lower() == "/post":
            try:
                await receiver(choice(PARSERS))
                await event.respond("Success!")
            except BaseException as e:
                logging.exception(e)
                await event.respond("Failed.")
        elif event.raw_text.lower() == "/suspend":
            global SUSPENDED
            SUSPENDED = not SUSPENDED
            await event.respond("Done! Status: " + str(SUSPENDED))


def main():
    loop.add_signal_handler(SIGINT, sys.exit, 0)
    loop.run_until_complete(
        asyncio.gather(
            loop.create_task(stdin_handler()), loop.create_task(worker())
        )
    )
