import discord
from typing import List

# Recover every image embeded or attached to a discord message
def message2images(message: discord.Message) -> List[str]:
	urls = []

	# Recover every image embeded in the message
	for embed in message.embeds:
		if embed.type == "image":
			urls.append(embed.url)

	# Recover every image attached to the message
	for attachment in message.attachments:
		if attachment.content_type.startswith("image/"):
			urls.append(attachment.url)

	return urls
