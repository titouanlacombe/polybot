import os

env = os.getenv("ENV")
in_dev = env.startswith("dev")
in_sta = env.startswith("sta")
in_pre = env.startswith("pre")
in_pro = env.startswith("pro")

ver = os.getenv("VER")
bot_token = os.getenv("BOT_TOKEN")

(polybot_host, polybot_port) = ("0.0.0.0", 5000)
(api_host, api_port) = ("api", 5001)

command_prefix = "/"
activity_update_interval = 15*60 # seconds

sentry_dsn = "https://eaea99bbc6e240caaf1cb2df8f90df82@o1391889.ingest.sentry.io/6712891"
