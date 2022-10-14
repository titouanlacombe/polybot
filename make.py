import re
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

# Add context to env
env(**env2dict(context_f))
_env = Environment(env("ENV"))

# Setup env
env(
	COMPOSE_PROJECT_NAME=f"{env('APP_NAME')}-{_env.short}-{env('VER').replace('.', '_')}",
	TZ="Europe/Paris",
	POLYBOT_PORT="8080",
	POLYBOT_API_PORT="5000",
	IMAGE_GEN_PORT="5001",
)

def get_arch():
	(_, out, err) = sh("rocminfo", throws=False, quiet=True).results()
	if re.search(r"Device Type:\s+GPU", out.decode("utf-8")):
		return "rocm"

	(_, out, err) = sh("nvidia-smi", throws=False, quiet=True).results()
	if re.search(r"GPU\s+Name:\s+.*", out.decode("utf-8")):
		return "cuda"

	return None

def arch_cache():
	if env("GPU_ARCH") is None:
		env(GPU_ARCH=get_arch() or "cpu")

def create_data():
	data.mkdir(exist_ok=True)
	logs.mkdir(exist_ok=True)
	static.mkdir(exist_ok=True)
	static_resources.mkdir(exist_ok=True)

def makever(ver: str):
	sh(f"git tag -a {ver} -m 'Version {ver}'")
	sh(f"git push origin {ver}")

def compose(cmd):
	files = ["./docker/docker-compose.yml"]
	files.append(f"./docker/docker-compose.{_env.short}.yml")
	
	arch_cache()
	if env("GPU_ARCH") != "cpu":
		files.append(f"./docker/docker-compose.{env('GPU_ARCH')}.yml")

	sh(f"docker-compose -f {' -f '.join(files)} {cmd}")

def prebuild():
	create_data()
	logo = Image.open(resources / "polybot.png")
	# logo = logo.convert("RGB")
	logo.save(static_resources / "polybot.png", "PNG", optimize=True, quality=85, progressive=True)
	logo.thumbnail((64, 64), Image.LANCZOS)
	logo.save(static / "favicon.ico", "PNG", optimize=True, quality=95, progressive=True)

	arch_cache()
	base_file = root/"docker"/"image-gen"/"Dockerfile"
	wfile(
		base_file,
		rfile(f"{base_file}.{env('GPU_ARCH')}")
		+ "\n\n"
		+ rfile(f"{base_file}.common")
	)

def build():
	prebuild()
	env(COMPOSE_DOCKER_CLI_BUILD="1", DOCKER_BUILDKIT="1")
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
