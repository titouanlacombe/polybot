from PIL import Image
from makepie import *

makepie_load()

# Setup filesystem
root = Path(".").resolve()
resources = root / "resources"
context_f = root / "context.env"
data = root.parent / "data"
logs = data / "logs"
app_resources = data / "resources"

# Add context to env
env(**env2dict(context_f))
_env = Environment(env("ENV"))

# Setup env
env(
	COMPOSE_PROJECT_NAME=f"{env('APP_NAME')}-{_env.short}-{env('VER').replace('.', '_')}",
)

def compose(cmd):
	files = ["./docker-compose.yml"]
	files.append(f"./docker-compose.{_env.short}.yml")

	sh(f"docker-compose -f {' -f '.join(files)} {cmd}")

def prebuild():
	data.mkdir(exist_ok=True)
	logs.mkdir(exist_ok=True)
	app_resources.mkdir(exist_ok=True)

	# Create different sized images
	logo = Image.open(resources / "polybot.png")
	logo.save(app_resources / "polybot.png", "PNG", optimize=True, quality=85, progressive=True)
	logo.thumbnail((64, 64), Image.LANCZOS)
	logo.save(app_resources / "favicon.ico", "PNG", optimize=True, quality=95, progressive=False)

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
def start():
	log(env("COMPOSE_PROJECT_NAME"))
	prebuild()
	build()
	up()
