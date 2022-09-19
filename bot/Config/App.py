import os

env = os.getenv("ENV")
ver = os.getenv("VER")
api_port = os.getenv("API_PORT")
polybot_port = os.getenv("POLYBOT_PORT")

def in_dev():
	return env.startswith("dev")

def in_sta():
	return env.startswith("sta")

def in_pre():
	return env.startswith("pre")

def in_pro():
	return env.startswith("pro")

command_prefix = "/"
activity_update_interval = 180 # seconds

# App color
color = "0x00ff00" # Green
if in_sta():
	color = "0x0000ff" # Blue
elif in_pre():
	color = "0xffa500" # Orange
elif in_pro():
	color = "0xff0000" # Red
