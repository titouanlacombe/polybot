import logging
from PIL import Image
from Config import precision_scope

log = logging.getLogger(__name__)

def set_default(dict, key, value):
	if key not in dict:
		dict[key] = value

# TODO Ordered by priority:
# Remove NSFW filter to save RAM
# ROCm: https://www.reddit.com/r/StableDiffusion/comments/ww436j/howto_stable_diffusion_on_an_amd_gpu/
# ROCm backup: https://www.gabriel.urdhr.fr/2022/08/28/trying-to-run-stable-diffusion-on-amd-ryzen-5-5600g/
# support image messages to allow for image2image
def text2img(pipeline, text: str, **kwargs) -> Image.Image:
	log.info(f"Generating image from '{text}', kwargs: {kwargs}")

	# Loading config
	# For info on args: https://huggingface.co/blog/stable_diffusion
	set_default(kwargs, "num_inference_steps", 15)
	set_default(kwargs, "guidance_scale", 7.5)
	set_default(kwargs, "width", 512)
	set_default(kwargs, "height", 512)

	# Generate image
	with precision_scope:
		pipe_out = pipeline(text, **kwargs)
	image: Image.Image = pipe_out.images[0]

	log.info("Image generated")

	# Save tmp image for debugging
	image.save("../data/tmp.png")

	log.info("Image encoded")
	return image
