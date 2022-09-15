import asyncio, discord, logging, aiohttp, unidecode, re
import random
from datetime import datetime
import Config.App as App
from discord.ext.commands import Bot
from .Trigger import Trigger

log = logging.getLogger(__name__)
random.seed()

def preprocess_text(text: str):
	# Replace accents
	text = unidecode.unidecode(text)
	text = text.lower()
	text = re.sub(r"[^a-z0-9 ]", " ", text)
	text = re.sub(r" +", " ", text)
	return text

# Dict to object
class MessageDummy:
	pass

class AuthorDummy:
	pass

def create_message(text, author):
	msg = MessageDummy()
	msg.content = text
	msg.author = AuthorDummy()
	msg.author.display_name = author
	msg.channel = None
	return msg

class PolyBot:
	def __init__(self, bot, triggers=[], presences=[], ignore_self=True):
		# Link discord client events
		self.bot: Bot = bot

		self.main_channel: discord.channel.TextChannel = None
		self.http_session = aiohttp.ClientSession()
		self.ignore_self = ignore_self

		self.ready = False
		self.paused = False
		self.up_since: datetime = datetime.now()
		self.triggers = triggers
		self.presences = presences

	def __del__(self):
		self.http_session.close()

	async def call_app(self, command, *args, **kwargs):
		log.info(f"Calling app: {command} {args} {kwargs}")
		async with self.http_session.post(f"http://0.0.0.0:{App.api_port}/rpc", json={
			"command": command,
			"args": args,
			"kwargs": kwargs
		}) as resp:
			log.debug(f"Received response from app: {resp}")
			return await resp.json()

	# --- API RPC ---
	async def pause(self):
		if self.paused:
			raise Exception("Bot is already paused")
		self.paused = True
		log.info("Bot paused")

	async def unpause(self):
		if not self.paused:
			raise Exception("Bot is not paused")
		self.paused = False
		log.info("Bot unpaused")

	# change presence wrapper
	async def change_presence(self, **kwargs):
		if App.in_pro():
			log.info(f"Setting presence: {kwargs}")
			await self.bot.change_presence(**kwargs)
		else:
			log.warning(f"Dry run, would set presence: {kwargs}")

	# channel.send wrapper
	async def send(self, message, channel=None):
		if message == "":
			raise Exception("Empty message")

		if not self.ready:
			raise Exception("Bot is not connected, can't talk")

		if self.paused:
			raise Exception("Bot is paused, no talking")
		
		if channel is None:
			channel = self.main_channel

		if channel is None:
			raise Exception("Can't talk: no channel specified and no main channel set")
		
		if App.in_pre():
			log.warning(f"Sending message to pre channel (original: {channel.name})")
			channel = discord.utils.get(self.get_all_channels(), name="polybot-preprod")

		if App.in_pro() or App.in_pre():
			log.info(f"Sending message: '{message}'")
			await channel.send(message)
		else:
			log.warning(f"Dry run, would send message: '{message}'")

	async def status(self):
		return {
			"ready": self.ready,
			"paused": self.paused,
			"up_since": self.up_since.strftime("%Y-%m-%d %H:%M:%S"),
			"env": App.env,
			"ver": App.ver,
		}

	async def handle_message(self, message):
		log.info(f"Handling message: {message.content}")

		# Ignore bot messages
		if self.ignore_self and message.author.display_name == self.bot.user.display_name:
			log.info(f"Ignoring message, author is polybot")
			return

		# TODO Check if we can remove this check
		# Check if the message is a command
		if message.content.startswith(App.command_prefix):
			log.debug(f"Message is a command, ignoring")
			return None

		processed = preprocess_text(message.content)
		log.debug(f"Processed text: '{processed}'")

		# Check if the message is a trigger
		trigger: Trigger
		for trigger in self.triggers:
			if trigger.triggered(message, processed):
				response = trigger.get_response(message)
				await self.send(response, message.channel)

				# Only one trigger per message
				return response

		log.info(f"No trigger found for message")

	# Function used to test bot response to a message
	async def message(self, text, author):
		return await self.handle_message(create_message(text, author))

	async def activity_loop(self):
		log.info(f"Starting activity loop, update interval: {App.activity_update_interval}")
		while True:
			await self.change_presence(activity=random.choice(self.presences))
			await asyncio.sleep(App.activity_update_interval)
			