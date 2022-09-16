import asyncio, logging, os, json, discord, sentry_sdk
import importlib
from discord.ext.commands import Bot

from Config.Filesystem import logs_dir
import Config.App as App
from Utils.Logging import basicConfig
from .PolyBot import PolyBot
from .BotCommands import register_commands
from .BotEvents import register_events
from .BotPresences import presences
from .BotTriggers import triggers
import Utils.Sentry as Sentry

basicConfig(logs_dir, "polybot", logging.INFO)
log = logging.getLogger(__name__)

Sentry.init()

poly_rpc_targets = [
	PolyBot.send.__name__,
	PolyBot.message.__name__,
	PolyBot.pause.__name__,
	PolyBot.unpause.__name__,
	PolyBot.status.__name__,
]

async def main():
	log.info(f"Starting discord client")

	# Setup
	# TODO search what are intents
	intents = discord.Intents.default()
	intents.message_content = True
	bot = Bot(command_prefix=App.command_prefix, intents=intents)

	try:
		secret_triggers_mod = importlib.import_module(".SecretTriggers", package="PolyBot")
		triggers.extend(secret_triggers_mod.triggers)
	except ModuleNotFoundError:
		log.warning("No secret triggers found")
		
	polybot = PolyBot(bot, triggers, presences)

	register_commands(polybot)
	register_events(polybot)

	async def request(request: asyncio.StreamReader, response: asyncio.StreamWriter):
		try:
			message_len = int.from_bytes(await request.readexactly(4), "big")
			message = await request.readexactly(message_len)
			data: dict = json.loads(message.decode())

			(command, args, kwargs) = (data["command"], data.get("args", []), data.get("kwargs", {}))
			log.info(f"Received rpc command: {command}({args}, {kwargs})")

			if command not in poly_rpc_targets:
				raise Exception(f"Unknown RPC command '{command}'")
			result = await getattr(polybot, command)(*args, **kwargs)

			resp = json.dumps({
				"result": result,
			})
			log.info(f"Sending rpc response: {resp}")
			response.write(resp.encode())
			
		except Exception as e:
			log.exception("Exception during request")
			sentry_sdk.capture_exception(e)
			resp = json.dumps({
				"error": str(e)
			})
			response.write(resp.encode())

	server = await asyncio.start_server(
		request,
		"0.0.0.0",
		App.polybot_port
	)
	
	# Start the discord client
	await bot.start(os.getenv("BOT_TOKEN"))

	# Start asyncio server
	await server.serve_forever()

asyncio.run(main())
