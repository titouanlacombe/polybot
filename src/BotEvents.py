import asyncio, logging, discord, datetime
from discord.ext.commands import Bot, Context
from PolyBot import PolyBot

import config.App as App

log = logging.getLogger(__name__)

async def set_message_example(polybot: PolyBot):
	log.info(f"Searching for message example")
	async for message in polybot.main_channel.history(limit=10):
		if not message.author.bot:
			polybot.message_example = message
			break

def register_events(polybot: PolyBot):
	bot: Bot = polybot.bot

	@bot.event
	async def on_ready():
		log.info(f"Logged on as '{bot.user}'")

		# Set channels
		channels = bot.get_all_channels()
		polybot.main_channel = discord.utils.get(channels, name="général")
		polybot.preprod_channel = discord.utils.get(channels, name="polybot-preprod")
		polybot.releases_channel = discord.utils.get(channels, name="polybot-releases")

		# Requirements satisfied
		polybot.ready = True

		# Launch activity loop
		asyncio.create_task(polybot.activity_loop())
		
		# Set online
		await asyncio.gather(
			polybot.change_presence(status=discord.Status.online),
			polybot.send(f"Polybot {App.ver} is online", channel=polybot.releases_channel),
			set_message_example(polybot),
		)

		boot_time = datetime.datetime.now() - polybot.up_since
		log.info(f"Polybot booted in: {int(boot_time.total_seconds() * 1000)} ms")

	@bot.event
	async def on_disconnect():
		log.info("Disconnected")
		polybot.ready = False
		
	@bot.event
	async def on_resumed():
		log.info("Resumed connexion")
		polybot.ready = True

	@bot.event
	async def on_message(message: discord.Message):
		log.info(f"Received message: \"{message.content}\"")
		
		if App.in_dev:
			log.info(f"Ignoring message, app in dev")
			return

		await polybot.handle_message(message)

	@bot.event
	async def on_error(event_method, *args, **kwargs):
		log.exception(f"Error while calling {event_method}, args: {args}, kwargs: {kwargs}")

	@bot.event
	async def on_command_error(ctx: Context, error):
		log.exception(f"Error while executing command", exc_info=error)
		await polybot.send("Error: " + str(error), reply_to=ctx.message)

