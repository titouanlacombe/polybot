from PIL import Image
from makepie import *

makepie_load()

# Setup filesystem
root = Path(".").resolve()
data = root.parent / "data"
logs = data / "logs"
static = root / "bot" / "static"
static_resources = static / "resources"
resources = root / "resources"
context_f = root / "context.env"

# TODO move to makepie
def load_env(f: Path):
	env = {}
	with open(f) as stream:
		for line in stream:
			if line.startswith("#"):
				continue
			k, v = line.split("=", 1)
			env[k] = v
	return env

# Add context to env
env(**load_env(context_f))
_env = Environment(env("ENV"))

# Setup env
env(
	COMPOSE_PROJECT_NAME=f"{env('APP_NAME')}-{_env.short}-{env('VER').replace('.', '_')}",
	TZ="Europe/Paris",
)

def create_data():
	data.mkdir(exist_ok=True)
	logs.mkdir(exist_ok=True)
	static.mkdir(exist_ok=True)
	static_resources.mkdir(exist_ok=True)

def makever(ver: str):
	sh(f"git tag -a {ver} -m 'Version {ver}'")
	sh(f"git push origin {ver}")

def compose(cmd):
	sh(f"docker-compose -f ./docker/docker-compose.yml -f ./docker/docker-compose.{_env.short}.yml {cmd}")

def prebuild():
	create_data()
	logo = Image.open(resources / "polybot.png")
	# logo = logo.convert("RGB")
	logo.save(static_resources / "polybot.png", "PNG", optimize=True, quality=85, progressive=True)
	logo.thumbnail((64, 64), Image.LANCZOS)
	logo.save(static / "favicon.ico", "PNG", optimize=True, quality=95, progressive=True)

def build():
	prebuild()
	compose("build")

def up():
	compose("up -d")

def down():
	compose("down")

def attach(target):
	compose(f"exec -it {target} bash")

@default()
def build_up():
	log(f"{env('APP_NAME')}-{_env.short}@{env('VER')}")
	build()
	up()
