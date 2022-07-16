from asyncio import sleep, get_event_loop
from datetime import datetime
from random import choice
from pyrogram import Client
from pyrogram.errors import BadRequest
from .dubctl import DubsDataFile
from .parser import UserCli, PARSERS
from .parser.base import WebParserTemplate, TgParserTemplate, ReceiveError
from . import utils, config

client = Client('.nekoposter',
                config.API_ID,
                config.API_HASH,
                bot_token=config.BOT_TOKEN)
client.start()
channel = config.CHANNEL
log_chat = config.LOG_CHAT
dublicates = DubsDataFile()

loop = get_event_loop()
loop.run_until_complete(dublicates._post_init())


async def post(file, test=False):
    out = channel if not test else log_chat
    counter = 0
    while counter < 3:
        counter += 1
        try:
            if file.startswith(('http:', 'https:')):
                await client.send_photo(out, file)
            else:
                await UserCli.send_cached_media(out, file)
            return
        except BadRequest:
            continue
    raise ReceiveError(str(file) + " is too big or unreachable.")


async def log(level, text):
    out = f'[{level}] {text}'
    print(out)
    await client.send_message(log_chat, '`' + out + '`')


async def wait():
    await sleep((60 - datetime.now().minute) * 60)


async def receiver(parser: WebParserTemplate or TgParserTemplate):
    if config.FALLBACK:
        async for latest_msg in UserCli.get_chat_history(config.CHANNEL, 1):
            if (datetime.now() - latest_msg.date).seconds < config.FALLBACK_TIMEOUT:
                return
    try:
        file = await parser.recv()
    except ReceiveError:
        parsers = list(PARSERS)
        parsers.remove(parser)
        if not parsers:
            parsers = PARSERS
        return await receiver(choice(parsers))
    if isinstance(file, int):
        dub_candidate = str(parser.chat.id) + ':' + str(file)
        if dub_candidate in dublicates.data:
            return await receiver(choice(PARSERS))
        msg = await UserCli.get_messages(parser.chat.id, file)
        media = utils.get_media(msg)
        if not media:
            return await receiver(choice(PARSERS))
        file = media.file_id
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
    await log("I", "started")
    while True:
        try:
            await receiver(choice(PARSERS))
        except BaseException as e:
            await log('E', e)
        await wait()


def main():
    loop.run_until_complete(worker())
