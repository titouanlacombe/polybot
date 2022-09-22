from io import BytesIO
import logging
from PIL import Image
from torch import autocast
from Config import device

log = logging.getLogger(__name__)

def set_default(dict, key, value):
	if key not in dict:
		dict[key] = value

# Ordered by priority:
# TODO how to make a discord proggress bar
# TODO support json text to allow for model tweaking per message (or parse message intent in polybot)
# TODO support image input to allow for image generation
def text2img(pipeline, text: str, **kwargs) -> bytes:
	log.info(f"Generating image from '{text}', kwargs: {kwargs}")

	# Loading config
	set_default(kwargs, "num_inference_steps", 15)

	# Generate image
	# with autocast(device.type):
	pipe_out = pipeline(text, **kwargs)
	image: Image.Image = pipe_out.images[0]

	# image = Image.new("RGB", (100, 100), (255, 0, 0))
	log.info("Image generated")

	# Return image as PNG bytes
	bytes = BytesIO()
	image.save(bytes, format="PNG")
	image_data = bytes.getvalue()

	log.info("Image encoded")
	return image_data
