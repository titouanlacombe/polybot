from PIL import Image
from makepie import *

makepie_load()

# Setup filesystem
root = Path(".").resolve()
resources = root / "resources"
context_f = root / "context.env"
data = root.parent / "data"
logs = data / "logs"
static = data / "static"

# Add context to env
env(**env2dict(context_f))
_env = Environment(env("ENV"))

# Setup env
env(
	COMPOSE_PROJECT_NAME=f"{env('APP_NAME')}-{_env.short}-{env('VER').replace('.', '_')}",
	POLYBOT_PORT="8080",
	POLYBOT_API_PORT="5000",
	IMAGE_GEN_PORT="5001",
)

def ver(_ver: str):
	sh(f"git tag -a {_ver} -m 'Version {_ver}'")
	sh(f"git push origin {_ver}")

def compose(cmd):
	files = ["./docker-compose.yml"]
	files.append(f"./docker-compose.{_env.short}.yml")

	sh(f"docker-compose -f {' -f '.join(files)} {cmd}")

def prebuild():
	data.mkdir(exist_ok=True)
	static.mkdir(exist_ok=True)

	# Create different sized images
	logo = Image.open(resources / "polybot.png")
	logo.save(static / "polybot.png", "PNG", optimize=True, quality=85, progressive=True)
	logo.thumbnail((64, 64), Image.LANCZOS)
	logo.save(static / "favicon.ico", "PNG", optimize=True, quality=95, progressive=False)

def build():
	compose("build")

def up():
	compose("up -d")

def down():
	compose("down")

def attach(target):
	compose(f"exec -it {target} bash")

@default()
def start():
	log(env("COMPOSE_PROJECT_NAME"))
	prebuild()
	build()
	up()
