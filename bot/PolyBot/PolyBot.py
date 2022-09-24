import asyncio, discord, logging, aiohttp, unidecode, re, base64, random, yaml
from io import BytesIO
from datetime import datetime
from discord.ext.commands import Bot

import Config.App as App
from .Trigger import Trigger
from .Message2Images import message2images
from .DiscordProggressBar import DiscordProgressBar

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
	dummy.id = random.randint(0, 2**64)
	dummy.author.name = author
	dummy.channel.name = channel
	return dummy

class PolyBot:
	def __init__(self, bot, triggers=[], presences=[], ignore_self=True):
		# Link discord client events
		self.bot: Bot = bot

		self.main_channel: discord.channel.TextChannel = None
		self.message_example: discord.Message = None
		self.http_session = aiohttp.ClientSession()
		self.ignore_self = ignore_self

		self.ready = False
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
		}) as resp:
			response: dict = await resp.json()
			log.debug(f"Response: {response}")

		if response.get("error") is not None:
			raise Exception(response["error"])

		return response["result"]

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

	async def send(self, content=None, **kwargs):
		kwargs["content"] = content

		if not self.ready:
			raise Exception("Bot is not connected, can't talk")

		if self.paused:
			raise Exception("Bot is paused, no talking")
		
		if kwargs.get("reply_to") is not None and kwargs.get("channel") is not None:
			raise Exception("Can't reply and send to a channel at the same time")

		if App.in_pre() and kwargs.get("channel") is not None:
			log.warning(f"Replacing channel to preprod channel (original: {kwargs['channel'].name})")
			kwargs["channel"] = discord.utils.get(self.bot.get_all_channels(), name="polybot-preprod")

		if App.in_dev() or App.in_sta():
			log.warning(f"Dry run, would send {kwargs}")
			return

		log.info(f"Sending {kwargs}")

		if kwargs.get("reply_to") is not None:
			return await kwargs.pop("reply_to").reply(**kwargs)

		if kwargs.get("channel") is None:
			if self.main_channel is None:
				raise Exception("Can't talk: no channel specified and no main channel set")
			kwargs["channel"] = self.main_channel
			return await kwargs.pop("channel").send(**kwargs)
		
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
				await self.send(response, reply_to=message)

				# Only one trigger per message
				return response

		log.info(f"No trigger found for message")
		return None

	async def handle_image_gen(self, message: discord.Message):
		image_gen_kwargs = {
			"request_id": message.id,
		}
		
		images = message2images(message)
		if len(images) > 0:
			if len(images) > 1:
				raise Exception("Too many images in message")
			image_gen_kwargs["image_url"] = images[0]

		if len(message.content) > 0:
			try:
				image_gen_kwargs.update(yaml.safe_load(message.content))
			except Exception as e:
				log.info(f"Failed to parse message content as YAML ({e}), assuming it's text")
				image_gen_kwargs["text"] = message.content

		resp: dict = await self.call_service(App.image_gen_host, "generate", **image_gen_kwargs)

		if resp.get("error", None) is not None:
			log.warning(f"Error occured in image-gen service: {resp}")
			await self.send(resp['error'], reply_to=message)
			return

		file_obj = BytesIO(base64.b64decode(resp['image'].encode("ascii")))

		await self.send(file=discord.File(file_obj, "image.png"), reply_to=message)

	async def pbar_create(self, request_id: int, total: int, title: str):
		request = self.get_request(request_id)

		async def send_callback(txt):
			await self.send(txt, reply_to=request['message'])

		bar = DiscordProgressBar(
			total=total,
			title=title,
			send_callback=send_callback
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
		log.info(f"Handling message: '{message.content}'")

		# Ignore bot messages
		if self.ignore_self and message.author.display_name == self.bot.user.display_name:
			log.debug(f"Ignoring message, author is polybot")
			return "Ignored"

		# Check if the message is a command
		if message.content.startswith(App.command_prefix):
			log.debug(f"Message is a command, handling...")
			self.requests[message.id]['type'] = "command"
			await self.bot.process_commands(message)
			return "Command handled"

		# Check if the message is posted in the image-gen channel
		if message.channel.name == "image-gen":
			log.debug(f"Message posted in image-gen channel, handling...")
			self.requests[message.id]['type'] = "image-gen"
			await self.handle_image_gen(message)
			return "Image generated"

		# Let message go through triggers
		trig = await self.handle_triggers(message)
		if trig is not None:
			self.requests[message.id]['type'] = "trigger"
			return f"Triggered '{trig}'"

		return "No response"

	async def handle_message(self, message: discord.Message):
		self.requests[message.id] = {
			"type": "unknown",
			"message": message,
		}
		await self._handle_message(message)
		del self.requests[message.id]

	# Function used to test bot response to a message
	async def message(self, text="", author="None", channel="general"):
		return await self.handle_message(create_message(self.message_example, text, author, channel))

	async def activity_loop(self):
		log.info(f"Starting activity loop, update interval: {App.activity_update_interval}")
		while True:
			await self.change_presence(activity=random.choice(self.presences))
			await asyncio.sleep(App.activity_update_interval)
			