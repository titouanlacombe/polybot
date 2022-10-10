import os

env = os.getenv("ENV")
ver = os.getenv("VER")

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

# env_color
env_color = "#1a9122" # Green
if in_sta():
	env_color = "#1a6a91" # Blue
elif in_pre():
	env_color = "#d98b25" # Orange
elif in_pro():
	env_color = "#de1616" # Red

image_gen_host = f"image-gen:{os.getenv('IMAGE_GEN_PORT')}"
polybot_host = f"localhost:{os.getenv('POLYBOT_PORT')}"
polybot_api_host = f"localhost:{os.getenv('POLYBOT_API_PORT')}"
