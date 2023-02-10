from makepie import *

makepie_load()

# Setup filesystem
root = Path(".").resolve()
context_f = root / "context.env"
data = root.parent / "data"
logs = data / "logs"

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

def build():
	prebuild()
	compose("build")

def up():
	sh(f"docker network create polybot-{_env.short}")
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
