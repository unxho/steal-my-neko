from configparser import ConfigParser


__config = ConfigParser()
__config.read("config.ini")

if not __config.sections():
    print("No config file found")
    raise SystemExit(1)

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
    raise SystemExit(1)
