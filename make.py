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

# Setup vars
_ver = root.name
_env = Environment(root.parent.name)
app_name = root.parent.parent.name
compose_project_name = f"{app_name}-{_env.short}-{_ver.replace('.', '_')}"

# Setup env
setenv(
	COMPOSE_PROJECT_NAME=compose_project_name,
	TZ="Europe/Paris",
	ENV=str(_env),
	VER=str(_ver),
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
	log(f"{app_name}-{_env} v{_ver}")
	build()
	up()
