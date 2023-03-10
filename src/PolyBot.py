import asyncio, discord, logging, aiohttp, unidecode, re, random, base64
from datetime import datetime
from discord.ext.commands import Bot
from io import BytesIO

import config.App as App
from Trigger import Trigger
from JokeGen import jokegen
from DiscordProggressBar import DiscordProgressBar

log = logging.getLogger(__name__)
random.seed()

def preprocess_text(text: str):
	# Replace accents
	text = unidecode.unidecode(text)
	text = text.lower()
	text = re.sub(r"[^a-z0-9 ]", " ", text)
	text = re.sub(r" +", " ", text)
	return text

# Warning: only works when proccessing one message at a time (because we modify the message in place)
def create_message(dummy: discord.Message, text, author, channel):
	dummy.content = text
	dummy.id = random.randint(1, 2**64)
	dummy.author.id = author
	dummy.channel.name = channel
	return dummy

class PolyBot:
	def __init__(self, bot, triggers=[], presences=[], ignore_self=True):
		# Link discord client events
		self.bot: Bot = bot

		self.main_channel: discord.channel.TextChannel = None
		self.preprod_channel: discord.channel.TextChannel = None
		self.releases_channel: discord.channel.TextChannel = None
		self.message_example: discord.Message = None
		self.http_session = aiohttp.ClientSession()
		self.timeout = aiohttp.ClientTimeout(total=900) # 15 minutes
		self.ignore_self = ignore_self

		self.ready = False
		self.api_token = None
		self.paused = False
		self.up_since: datetime = datetime.now()
		self.triggers = triggers
		self.presences = presences

		self.requests: dict = {}

	def get_request(self, request_id, expected_type=None):
		request = self.requests.get(request_id)
		if request is None:
			raise Exception(f"Unknown request id '{request_id}'")
		if expected_type is not None and request["type"] != expected_type:
			raise Exception(f"Invalid request type for id '{request_id}'")
		return request

	def __del__(self):
		self.http_session.close()

	async def call_service(self, host, command, *args, **kwargs):
		log.info(f"Calling {host}: {command}(*{args}, **{kwargs})")
		async with self.http_session.post(f"http://{host}/rpc", json={
			"command": command,
			"args": args,
			"kwargs": kwargs
		}, timeout=self.timeout) as resp:
			if not (resp.status >= 200 and resp.status < 300):
				raise Exception(f"Service call failed with status {resp.status}: {await resp.text()}")
			
			response: dict = await resp.json()
			log.debug(f"Response: {response}")

		if response.get("error") is not None:
			raise Exception(response["error"])

		return response["result"]

	async def get_auth_header(self):
		if self.api_token is None:
			async with self.http_session.post(f"{App.api_url}/api/token/", json={
					"username": App.api_account,
					"password": App.api_password
				}, timeout=self.timeout) as resp:
				if not (resp.status >= 200 and resp.status < 300):
					raise Exception(f"API auth failed with status {resp.status}: {await resp.text()}")

				response: dict = await resp.json()
			self.api_token = response["token"]
		return {
			"Authorization": f"Token {self.api_token}"
		}

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
		if App.in_pro:
			log.info(f"Setting presence: {kwargs}")
			await self.bot.change_presence(**kwargs)
		else:
			log.info(f"Dry run, would set presence: {kwargs}")

	def check_ready(self):
		if not self.ready:
			raise Exception("Bot is not connected, can't talk")
		if self.paused:
			raise Exception("Bot is paused, no talking")

	async def send(self, content=None, **kwargs):
		self.check_ready()
		kwargs["content"] = content

		if kwargs.get("reply_to") is not None and kwargs.get("channel") is not None:
			raise Exception("Can't reply and send to a channel at the same time")

		if App.in_dev or App.in_sta:
			log.info(f"Dry run, would send {kwargs}")
			return None

		if App.in_pre:
			kwargs.pop("reply_to", None)
			log.info(f"Replacing channel to preprod channel (original: {kwargs.get('channel')})")
			kwargs["channel"] = self.preprod_channel

		log.info(f"Sending {kwargs}")

		if kwargs.get("reply_to") is not None:
			message = await kwargs.pop("reply_to").reply(**kwargs)
		elif kwargs.get("channel") is not None:
			message = await kwargs.pop("channel").send(**kwargs)
		else:
			if self.main_channel is None:
				raise Exception("No target specified and main channel not set")
			message = await self.main_channel.send(**kwargs)

		return message

	async def edit(self, message: discord.Message, content=None, **kwargs):
		self.check_ready()
		kwargs["content"] = content

		if App.in_dev or App.in_sta:
			log.info(f"Dry run, would edit {message} to {kwargs}")
			return None

		if App.in_pre:
			if message.channel != self.preprod_channel:
				raise Exception("In preprod: can't edit message in prod channel")

		log.info(f"Editing {message} to {kwargs}")
		return await message.edit(**kwargs)

	async def delete(self, message: discord.Message):
		self.check_ready()

		if App.in_dev or App.in_sta:
			log.info(f"Dry run, would delete {message}")
			return None

		if App.in_pre:
			if message.channel != self.preprod_channel:
				raise Exception("In preprod: can't delete message in prod channel")

		log.info(f"Deleting {message}")
		return await message.delete()

	async def rpc_send(self, content=None, **kwargs):
		if kwargs.get("reply_to") is not None:
			kwargs["reply_to"] = self.get_request(kwargs["reply_to"])["message"]

		if kwargs.get("channel") is not None:
			kwargs["channel"] = discord.utils.get(self.bot.get_all_channels(), name=kwargs["channel"])

		files = kwargs.pop("files", [])
		kwargs["files"] = [discord.File(
			BytesIO(base64.b64decode(file["data"])),
			filename=file["name"],
		) for file in files]
		
		message = await self.send(content, **kwargs)
		return None if message is None else message.id

	async def status(self):
		return {
			"ready": self.ready,
			"paused": self.paused,
			"up_since": self.up_since.strftime("%Y-%m-%d %H:%M:%S"),
			"env": App.env,
			"ver": App.ver,
		}

	async def handle_triggers(self, message):
		processed = preprocess_text(message.content)
		log.debug(f"Processed text: '{processed}'")

		trigger: Trigger
		for trigger in self.triggers:
			if trigger.triggered(message, processed):
				response = trigger.get_response(message)

				# Only one trigger per message
				return await self.send(response, reply_to=message)

		log.info(f"No trigger found for message")
		return None

	async def handle_jokegen(self, message: discord.Message):
		if random.randrange(1, 200) >= 1:
			log.debug("Not triggering jokegen")
			return None
		
		log.info("Triggering jokegen")
		return await self.send(jokegen(message), channel=message.channel)

	async def pbar_create(self, request_id: int, total: int, title: str):
		request = self.get_request(request_id)

		bar = DiscordProgressBar(
			total=total,
			title=title,
			sender=self
		)
		request['progress_bar'] = bar

		await bar.start()

	async def pbar_update(self, request_id: int, current: int):
		request = self.get_request(request_id)
		bar: DiscordProgressBar = request['progress_bar']
		await bar.update(current)

	async def pbar_finish(self, request_id: int):
		request = self.get_request(request_id)
		bar: DiscordProgressBar = request['progress_bar']
		await bar.finish()

	async def _handle_message(self, message: discord.Message):
		log.debug(f"Handling message: \"{message.content}\"")

		# Ignore bot messages
		if self.ignore_self and message.author == self.bot.user:
			log.debug(f"Ignoring message, author is polybot")
			return "Ignored"

		# Check if the message is a command
		if message.content.startswith(App.command_prefix):
			log.debug(f"Message is a command, handling...")
			self.requests[message.id]['type'] = "command"
			await self.bot.process_commands(message)
			return "Command handled"

		# Let message go through triggers
		trig = await self.handle_triggers(message)
		if trig is not None:
			return "Triggered", trig

		# Joke generator
		joke = await self.handle_jokegen(message)
		if joke is not None:
			return "Joke", joke
		
		return "No response"

	async def handle_message(self, message: discord.Message):
		self.requests[message.id] = {
			"type": "unknown",
			"message": message,
		}
		res = await self._handle_message(message)
		del self.requests[message.id]
		return res

	# Function used to test bot response to a message
	async def message(self, text="", author=1, channel="general"):
		if self.message_example is None:
			raise Exception("No message example found (not loaded)")

		return await self.handle_message(create_message(self.message_example, text, author, channel))

	async def activity_loop(self):
		log.info(f"Starting activity loop, update interval: {App.activity_update_interval}")
		while True:
			await self.change_presence(activity=random.choice(self.presences))
			await asyncio.sleep(App.activity_update_interval)
	
	async def objectify_reaction(self, reaction: discord.Reaction):
		# Flatten users
		users = []
		async for user in reaction.users():
			users.append(user)

		return {
			"emoji": reaction.emoji,
			"count": reaction.count,
			"users": [user.id for user in users],
		}

	async def objectify_message(self, message: discord.Message):
		return {
			"id": message.id,
			"content": message.content,
			"channel": message.channel.id,
			"author": message.author.id,
			"reactions": [await self.objectify_reaction(reaction) for reaction in message.reactions],
			"timestamp": message.created_at.isoformat(),
		}

	async def scrap_messages(self, channel: str|None = None, limit: int = 200, date: str|None = None):
		if channel is None:
			channel = self.main_channel.name

		channel: discord.TextChannel = discord.utils.get(self.bot.get_all_channels(), name=channel)
		if channel is None:
			raise Exception(f"Channel '{channel}' not found")

		if date is not None:
			date = datetime.fromisoformat(date)
		else:
			date = None

		messages = []
		async for message in channel.history(limit=limit, after=date, oldest_first=True):
			messages.append(await self.objectify_message(message))

		return messages
