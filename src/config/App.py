import os

env = os.getenv("ENV")
in_dev = env.startswith("dev")
in_sta = env.startswith("sta")
in_pre = env.startswith("pre")
in_pro = env.startswith("pro")

ver = os.getenv("VER")
bot_token = os.getenv("BOT_TOKEN")

(polybot_host, polybot_port) = ("0.0.0.0", 5000)
(api_host, api_port) = ("0.0.0.0", 5001)
imagen_url = "" # TODO

env_color = "#1a9122" # Green
if in_sta: env_color = "#1a6a91" # Blue
elif in_pre: env_color = "#d98b25" # Orange
elif in_pro: env_color = "#de1616" # Red

command_prefix = "/"
activity_update_interval = 15*60 # seconds

sentry_dsn = "https://eaea99bbc6e240caaf1cb2df8f90df82@o1391889.ingest.sentry.io/6712891"
