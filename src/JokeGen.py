import discord, logging

log = logging.getLogger(__name__)

def format_message(message: discord.Message):
	return f"{message.author.name}: {message.content}\n"

def jokegen(message: discord.Message):
	# Get history
	history = message.channel.history(limit=20)

	# Generate prompt from history
	prompt = ""
	for message in history:
		prompt += format_message(message)

	# Send prompt to GPT-3
	log.info(f"Sending prompt to GPT-3: {prompt}")

	# TODO: Implement GPT-3

	response = "This is a response from GPT-3"
	log.info(f"Got response from GPT-3: {response}")
	
	# Send response to channel
	return response
