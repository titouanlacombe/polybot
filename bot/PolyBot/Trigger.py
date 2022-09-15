import logging
import re
import random
from discord import Message

log = logging.getLogger(__name__)

class Trigger:
	def __init__(
		self,
		regex,
		get_response,
		special_users = None,
		random_chance = 1,
		preprocess_text = True
	):
		self.regex = re.compile(regex, re.IGNORECASE)
		self.get_response = get_response
		self.special_users = special_users
		self.random_chance = random_chance
		self.preprocess_text = preprocess_text

	def get_text(self, message: Message, processed):
		if self.preprocess_text:
			return processed
		else:
			return message.content

	def triggered(self, message: Message, processed):
		log.debug(f"Checking trigger {self}")
		
		# Check if the message matches the regex
		if not self.regex.search(self.get_text(message, processed)):
			log.debug(f"Regex failed")
			return False

		# If special users whitelist is set, check if the user is in it
		if self.special_users and message.author.display_name not in self.special_users:
			log.debug(f"User whitelist failed")
			return False

		# Execute random chance (message will have a chance of being ignored)
		if random.random() > self.random_chance:
			log.debug(f"Random failed")
			return False

		log.debug(f"Success")
		return True

	def __str__(self) -> str:
		return f"{self.regex.pattern}"
