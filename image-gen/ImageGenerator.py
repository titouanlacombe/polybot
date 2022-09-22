from io import BytesIO
import logging
from PIL import Image
from Config import precision_scope

log = logging.getLogger(__name__)

def set_default(dict, key, value):
	if key not in dict:
		dict[key] = value

# Ordered by priority:
# TODO ROCm: https://www.reddit.com/r/StableDiffusion/comments/ww436j/howto_stable_diffusion_on_an_amd_gpu/
# TODO ROCm backup: https://www.gabriel.urdhr.fr/2022/08/28/trying-to-run-stable-diffusion-on-amd-ryzen-5-5600g/
# TODO how to make a discord proggress bar
# TODO support json text to allow for model tweaking per message (or parse message intent in polybot)
# TODO support image input to allow for image generation
def text2img(pipeline, text: str, **kwargs) -> bytes:
	log.info(f"Generating image from '{text}', kwargs: {kwargs}")

	# Loading config
	set_default(kwargs, "num_inference_steps", 15)

	# Generate image
	with precision_scope:
		pipe_out = pipeline(text, **kwargs)
	image: Image.Image = pipe_out.images[0]

	log.info("Image generated")

	# Save tmp image for debugging
	image.save("../data/tmp.png")

	# Return image as PNG bytes
	bytes = BytesIO()
	image.save(bytes, format="PNG")
	image_data = bytes.getvalue()

	log.info("Image encoded")
	return image_data
