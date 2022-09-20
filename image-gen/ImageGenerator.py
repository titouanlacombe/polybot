from io import BytesIO
import logging
import os
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch

# TODO fix permissions by learning about bitnami default user
log = logging.getLogger(__name__)

# TODO support json text to allow for model tweaking per message
# TODO support image input to allow for image generation
# TODO how to make a discord proggress bar
# TODO add semaphore to limit the number of running jobs
def text2img(text: str):
	log.info(f"Generating from '{text}'")

	# Setup pipeline
	pipe = StableDiffusionPipeline.from_pretrained(
		"CompVis/stable-diffusion-v1-4",
		use_auth_token=os.getenv("HF_TOKEN"),

		# Optimization because i have no RAM :'(
		# TODO how to fix fp16 on the CPU
		revision="fp16",
		torch_dtype=torch.float16,
	)
	pipe.to("cpu")

	log.info("Pipe initialized")
	
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
