from asyncio import sleep, get_event_loop
from datetime import datetime
from random import choice
import logging
from telethon import TelegramClient
from telethon.errors import BadRequestError
from telethon.tl.custom.message import Message
from .dubctl import DubsDataFile
from .parser import UserCli, PARSERS
from .parser.base import WebParserTemplate, TgParserTemplate, ReceiveError
from . import config, log

client = TelegramClient('.nekoposter', config.API_ID, config.API_HASH)
client.start(bot_token=config.BOT_TOKEN)

channel = config.CHANNEL
log_chat = config.LOG_CHAT
dublicates = DubsDataFile()

loop = get_event_loop()
loop.run_until_complete(dublicates._post_init())
log.init(client)


async def post(file, test=False):
    out = channel if not test else log_chat
    counter = 0
    while counter < 3:
        counter += 1
        try:
            if isinstance(file, str) and file.startswith(('http:', 'https:')):
                await client.send_message(out, file=file)
            else:
                await UserCli.send_message(out, file=file)
            return
        except BadRequestError:
            continue
    raise ReceiveError(str(file) + " is too big or unreachable.")


async def wait():
    await sleep((60 - datetime.now().minute) * 60)


async def receiver(parser: WebParserTemplate or TgParserTemplate):
    if config.FALLBACK:
        async for latest_msg in UserCli.iter_messages(config.CHANNEL, 1):
            if ((datetime.now() - latest_msg.date).seconds <
                    config.FALLBACK_TIMEOUT):
                return
    try:
        file = await parser.recv()
    except ReceiveError:
        parsers = list(PARSERS)
        parsers.remove(parser)
        if not parsers:
            parsers = PARSERS
        return await receiver(choice(parsers))
    if isinstance(file, Message):
        file = [file]
    if isinstance(file, list):
        file_ = file
        file = []
        for f in file_:
            dub_candidate = str(parser.chat.id) + ':' + str(f.id)
            if dub_candidate in dublicates.data or not f.media:
                return await receiver(choice(PARSERS))
            file.append(f.media)
    else:
        dub_candidate = file.split('/')[-1]
        if dub_candidate in dublicates.data:
            return await receiver(choice(PARSERS))
    await dublicates.update(dub_candidate)
    try:
        return await post(file)
    except ReceiveError:
        return await receiver(choice(PARSERS))


async def worker():
    logging.info("Launched.")
    while True:
        try:
            await receiver(choice(PARSERS))
        except BaseException as e:
            logging.error(e)
        await wait()


def main():
    loop.run_until_complete(worker())
