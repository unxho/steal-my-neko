try:
    import orjson as json
except (ImportError, ModuleNotFoundError):
    import json

try:
    with open('config.json', 'r', encoding='utf8') as f:
        __config = json.loads(f.read())
except FileNotFoundError as e:
    raise ValueError("No config file found") from e

API_ID, API_HASH = __config['API_ID'], __config['API_HASH']
BOT_TOKEN = __config['BOT_TOKEN']
HELPER_PHONE = __config.get('HELPER_PHONE')
CHANNEL, LOG_CHAT = __config['CHANNEL'], __config['LOG_CHAT']
