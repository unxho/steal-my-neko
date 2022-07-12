from configparser import ConfigParser

__config = ConfigParser()

try:
    __config.read('config.ini')
except FileNotFoundError as e:
    raise ValueError("No config file found") from e

API_ID, API_HASH = __config.get("api", "id"), __config.get("api", "hash")
BOT_TOKEN = __config.get("bot", "token")
HELPER_ENABLED, HELPER_PHONE = __config.get("helper", "use"), \
                               __config.get("helper", "phone")
CHANNEL, LOG_CHAT = __config.get("target", "channel"), \
                    __config.get("target", "log_chat")
