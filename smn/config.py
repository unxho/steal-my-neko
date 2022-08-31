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

FREQUENCY = [int(i) for i in __config.get("posting", "frequency").split(",")]
FREQUENCY_AS_RANGE = __config.getboolean("posting", "frequency_as_range")
POST_ON_FIRST_RUN = __config.getboolean("posting", "post_on_first_run")
WAIT_UNTIL_NEW_HOUR = __config.getboolean(
    "posting", "wait_until_new_hour_first"
)

ADMIN = __config.getint("admin", "id")

if not HELPER_ENABLED and FALLBACK:
    print("CONFIG CONFLICT: HELPER MUST BE PRESENT TO USE FALLBACK MODE")
    raise SystemExit(1)
