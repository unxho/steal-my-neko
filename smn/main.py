import asyncio
from datetime import datetime
from random import choice
import logging
import sys
from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.errors import BadRequestError, FileReferenceExpiredError
from .dubctl import DubsDataFile
from .parser import UserCli, PARSERS
from .parser.base import WebParserTemplate, TgParserTemplate, ReceiveError
from . import config, log

client = TelegramClient(".nekoposter", config.API_ID, config.API_HASH)
client.start(bot_token=config.BOT_TOKEN)

channel = config.CHANNEL
log_chat = config.LOG_CHAT
dublicates = DubsDataFile()

loop = asyncio.get_event_loop()
loop.run_until_complete(dublicates._post_init())
log.init(client)
suspended = False


async def post(file, test=False, ids=None, entity=None):
    out = channel if not test else log_chat
    counter = 0
    while counter < 3:
        counter += 1
        try:
            if isinstance(file, str) and file.startswith(("http:", "https:")):
                await client.send_message(out, file=file)
            else:
                if isinstance(file, list) and len(file) == 1:
                    file = file[0]
                await UserCli.send_message(out, file=file)
            return
        except FileReferenceExpiredError:
            logging.debug("File reference expired, refetching messages...")
            file = []
            # refetching outdated messages
            async for m in UserCli.iter_messages(entity, ids=ids):
                file.append(m.media)
            continue
        except BadRequestError as e:
            logging.debug(e)
            continue
    raise ReceiveError(str(file) + " is too big or unreachable.")


async def wait():
    seconds = (60 - datetime.now().minute) * 60
    logging.debug("Waiting: " + str(seconds))
    await asyncio.sleep(seconds)


async def receiver(parser: WebParserTemplate or TgParserTemplate):
    """
    Main parse wrapper.

    Message/list - list of messages
    str          - link to file
    bytes        - file data
    """
    if config.FALLBACK:
        async for latest_msg in UserCli.iter_messages(config.CHANNEL, 1):
            if (datetime.now() - latest_msg.date).seconds < config.FALLBACK_TIMEOUT:
                return
    try:
        file = await parser.recv()
    except ReceiveError as e:
        logging.debug(e)
        parsers = list(PARSERS)
        parsers.remove(parser)
        if not parsers:
            parsers = PARSERS
        return await receiver(choice(parsers))
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
        entity = parser.chat
        for f in file_:
            dub_candidate = str(parser.chat.id) + ":" + str(f.id)
            if dub_candidate in dublicates.data or not f.media:
                logging.debug("Dublicate: " + dub_candidate)
                return await receiver(choice(PARSERS))
            msg_ids.append(f.id)
            file.append(f.media)
    elif isinstance(file, str):
        # Link
        dub_candidate = file.split("/")[-1]
        if dub_candidate in dublicates.data:
            logging.debug("Dublicate: " + dub_candidate)
            return await receiver(choice(PARSERS))
    # elif isinstance(file, bytes):
    # TODO: raw data does not support dublicate checks
    if dub_candidate:
        await dublicates.update(dub_candidate)
    try:
        return await post(file, ids=msg_ids, entity=entity)
    except ReceiveError:
        return await receiver(choice(PARSERS))


async def worker():
    logging.info("Launched.")
    while True:
        if suspended:
            await wait()
            continue
        try:
            await receiver(choice(PARSERS))
        except BaseException as e:
            logging.exception(e)
        await wait()


async def stdin_handler():
    print(
        "Hello!\nSteal My Neko control commands:\n"
        "- post - to force a post\n- suspend - to (un)suspend posting\n- exit - to finish this program.\n\n"
    )
    while True:
        msg = (await loop.run_in_executor(None, input)).lower()
        if msg == "post":
            try:
                await receiver(choice(PARSERS))
                print("Success!")
            except BaseException as e:
                logging.exception(e)
                print("Failed.")
        elif msg == "suspend":
            global suspended
            suspended = not suspended
            print("Done! Status:", suspended)
        elif msg == "exit":
            print("Bye-bye.")
            sys.exit(0)


if config.ADMIN:

    @client.on(
        NewMessage(from_users=config.ADMIN, incoming=True, func=lambda m: m.raw_text)
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
            global suspended
            suspended = not suspended
            await event.respond("Done! Status: " + str(suspended))


def main():

    tasks = (loop.create_task(worker()), loop.create_task(stdin_handler()))
    loop.run_until_complete(asyncio.gather(*tasks))
