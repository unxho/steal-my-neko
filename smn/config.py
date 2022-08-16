from configparser import ConfigParser
import os
import sys

__config = ConfigParser()
if "config.ini" not in os.listdir():
    print("No config file found")
    sys.exit(1)
__config.read("config.ini")

API_ID = __config.getint("api", "id")
API_HASH = __config.get("api", "hash")

BOT_TOKEN = __config.get("bot", "token")

HELPER_ENABLED = __config.getboolean("helper", "use")

CHANNEL = __config.getint("target", "channel")
LOG_CHAT = __config.getint("target", "log_chat")

FALLBACK = __config.getboolean("posting", "fallback")
FALLBACK_TIMEOUT = __config.getint("posting", "fallback_timeout")

ADMIN = __config.getint("admin", "id")

if not HELPER_ENABLED and FALLBACK:
    print("CONFIG CONFLICT: HELPER MUST BE PRESENT TO USE FALLBACK MODE")
    sys.exit(1)
