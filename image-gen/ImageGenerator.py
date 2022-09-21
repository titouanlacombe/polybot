from io import BytesIO
import logging
from PIL import Image
from setup_pipeline import pipe

# Loading pipe
pipe.to("cpu")

# TODO fix permissions by learning about bitnami default user
log = logging.getLogger(__name__)

# TODO support json text to allow for model tweaking per message
# TODO support image input to allow for image generation
# TODO how to make a discord proggress bar
# TODO add semaphore to limit the number of running jobs
def text2img(text: str):
	log.info(f"Generating from '{text}'")

	# Generate image
	# results = pipe(text, num_inference_steps=15)
	# image = results.images[0]
	image = Image.new("RGB", (100, 100), (255, 0, 0))
	log.info("Image generated")

	# Return image as PNG bytes
	bytes = BytesIO()
	image.save(bytes, format="PNG")
	image_data = bytes.getvalue()

	log.info("Image encoded")
	return image_data
