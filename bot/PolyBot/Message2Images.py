import asyncio, discord, aiohttp
from io import BytesIO
from typing import List
from PIL import Image

async def open_image(url: str, http_session: aiohttp.ClientSession) -> Image.Image:
	resp = await http_session.get(url)
	file_obj = BytesIO(await resp.read())
	return Image.open(file_obj)

# Recover every image embeded or attached to a discord message
async def message2images(message: discord.Message, http_session) -> List[Image.Image]:
	urls = []

	# Recover every image embeded in the message
	for embed in message.embeds:
		if embed.type == "image":
			urls.append(embed.url)

	# Recover every image attached to the message
	for attachment in message.attachments:
		if attachment.content_type.startswith("image/"):
			urls.append(attachment.url)

	return await asyncio.gather(*[open_image(url, http_session) for url in urls])
