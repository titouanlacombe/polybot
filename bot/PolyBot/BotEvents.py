import asyncio
import logging, discord
from discord.ext.commands import Bot, Context
from .PolyBot import PolyBot

import Config.App as App

log = logging.getLogger(__name__)

def register_events(polybot: PolyBot):
	bot: Bot = polybot.bot

	@bot.event
	async def on_ready():
		log.info(f"Logged on as '{bot.user}'")

		status = discord.Status.online if App.in_pro() else discord.Status.invisible
		log.info(f"Setting status to {status}")		
		await polybot.change_presence(status=status)

		# Set main channel
		polybot.main_channel = discord.utils.get(bot.get_all_channels(), name="général")

		# Launch activity loop
		asyncio.create_task(polybot.activity_loop())

		polybot.ready = True

	@bot.event
	async def on_disconnect():
		log.info("Disconnected")
		polybot.ready = False
		
	@bot.event
	async def on_resume():
		log.info("Resumed connexion")
		polybot.ready = True

	@bot.event
	async def on_message(message: discord.Message):
		log.info(f"Received message: {message.content}")
		
		if App.in_dev():
			log.info(f"Ignoring message, app in dev")
			return

		await polybot.handle_message(message)

	@bot.event
	async def on_error(event_method, *args, **kwargs):
		log.exception(f"Error while calling {event_method}, args: {args}, kwargs: {kwargs}")

	@bot.event
	async def on_command_error(ctx: Context, error):
		log.exception(f"Error while executing command")
		await polybot.send("Error: " + str(error), ctx.channel)

