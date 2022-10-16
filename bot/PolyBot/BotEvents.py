import asyncio, logging, discord, datetime
from discord.ext.commands import Bot, Context
from .PolyBot import PolyBot

import Config.App as App

log = logging.getLogger(__name__)

async def set_status(polybot: PolyBot, status: discord.Status):
	status = discord.Status.online if App.in_pro() else discord.Status.invisible
	log.info(f"Setting status to {status}")
	await polybot.bot.change_presence(status=status)

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
		polybot.main_channel = discord.utils.get(bot.get_all_channels(), name="général")
		polybot.preprod_channel = discord.utils.get(bot.get_all_channels(), name="polybot-preprod")

		# Launch activity loop
		asyncio.create_task(polybot.activity_loop())

		# Gather api requests
		asyncio.gather(
			set_status(polybot, discord.Status.online),
			set_message_example(polybot),
		)

		polybot.ready = True

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
		
		if App.in_dev():
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

