from configparser import ConfigParser
import os

__config = ConfigParser()
if 'config.ini' not in os.listdir():
    print("No config file found")
    exit(1)
__config.read('config.ini')

API_ID, API_HASH = __config.get("api", "id"), __config.get("api", "hash")
BOT_TOKEN = __config.get("bot", "token")
HELPER_ENABLED, HELPER_PHONE = __config.get("helper", "use"), \
                               __config.get("helper", "phone")
CHANNEL, LOG_CHAT = __config.get("target", "channel"), \
                    __config.get("target", "log_chat")
FALLBACK, FALLBACK_TIMEOUT = __config.get("posting", "fallback"), \
                             __config.get("posting", "fallback_timeout")

if not HELPER_ENABLED and FALLBACK:
    print('CONFIG CONFLICT: HELPER MUST BE PRESENT TO USE FALLBACK MODE')
    exit(1)
