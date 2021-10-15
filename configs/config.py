import os


LOGFILE = os.environ.get("LOGFILE", "C:/Users/LENOVO/AppData/Local/Temp")

SIGNING_SECRET = os.environ.get("SIGNING_SECRET")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_BOT_NAME = os.environ.get("SLACK_BOT_NAME", "SAB")
DEFAULT_SLACK_CHANNEL = os.environ.get("DEFAULT_SLACK_CHANNEL", "#test")

# Pytz timezone string. You can see a full list here:
# https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568
# or by calling pytz.all_timezones
TIMEZONE = "Asia/Saigon"

# Valid 2 letter The 2-letter ISO 3166-1 code (lowercase).
# E.g. "us" for USA. Defaults to all.
COUNTRY_CODE = "vn"