# Setting up logging before anything else
import logging, logging.config
import config.Logging as Logging
logging.config.dictConfig(Logging.get_dict_conf('polybot'))

import asyncio, json, discord, sentry_sdk, importlib, signal
from discord.ext.commands import Bot

import config.App as App
from PolyBot import PolyBot
from BotCommands import register_commands
from BotEvents import register_events
from BotPresences import presences
from BotTriggers import triggers


log = logging.getLogger(__name__)

sentry_sdk.init(
	dsn=App.sentry_dsn,
	integrations=[],

	# Set traces_sample_rate to 1.0 to capture 100%
	# of transactions for performance monitoring.
	# We recommend adjusting this value in production.
	traces_sample_rate=1.0,
	environment=App.env,
	release=App.ver,
)

poly_rpc_targets = [
	PolyBot.rpc_send.__name__,
	PolyBot.message.__name__,
	PolyBot.pause.__name__,
	PolyBot.unpause.__name__,
	PolyBot.status.__name__,
	PolyBot.pbar_create.__name__,
	PolyBot.pbar_update.__name__,
	PolyBot.pbar_finish.__name__,
	PolyBot.scrap_messages.__name__,
]

async def main():
	log.info(f"Starting discord client")

	# Setup
	intents = discord.Intents.default()
	intents.message_content = True
	bot = Bot(command_prefix=App.command_prefix, intents=intents)

	try:
		secret_triggers_mod = importlib.import_module(".SecretTriggers", package="polybot")
		triggers.extend(secret_triggers_mod.triggers)
	except ModuleNotFoundError:
		log.warning("No secret triggers found")
		
	polybot = PolyBot(bot, triggers, presences)

	register_commands(polybot)
	register_events(polybot)

	async def process_request(request: asyncio.StreamReader, response: asyncio.StreamWriter):
		try:
			message_len = int.from_bytes(await request.readexactly(4), "big")
			message = await request.readexactly(message_len)
			data: dict = json.loads(message.decode())

			(procedure, args, kwargs) = (data["procedure"], data.get("args", []), data.get("kwargs", {}))
			log.debug(f"Received rpc procedure: {procedure}({args}, {kwargs})")

			if procedure not in poly_rpc_targets:
				raise Exception(f"Unknown RPC procedure '{procedure}'")
				
			resp = {
				"result": await getattr(polybot, procedure)(*args, **kwargs),
			}
		except Exception as e:
			log.exception("Exception during request")
			sentry_sdk.capture_exception(e)
			resp = {
				"error": str(e)
			}

		resp = json.dumps(resp).encode()
		log.debug(f"Sending rpc response: {resp}")
		response.write(resp)
		response.close()

	# Create the socket server & start the discord client
	server: asyncio.AbstractServer
	(server, _) = await asyncio.gather(
		asyncio.start_server(
			process_request,
			App.polybot_host, App.polybot_port,
		),
		bot.start(App.bot_token),
	)

	# Start socket server
	await server.serve_forever()

# Stop on SIGINT or SIGTERM
def stop():
	log.info("Stopping discord client")
	exit(0)

signal.signal(signal.SIGINT, lambda sig, frame: stop())
signal.signal(signal.SIGTERM, lambda sig, frame: stop())

try:
	asyncio.run(main())
except Exception as e:
	log.exception("Exception during main")
	sentry_sdk.capture_exception(e)
