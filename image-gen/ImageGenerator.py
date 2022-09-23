import logging, base64
from threading import Thread
from io import BytesIO
from werkzeug.exceptions import ServiceUnavailable
from PIL import Image

from Config import precision_scope
from Microservices import call_rpc

log = logging.getLogger(__name__)

def set_default(dict, key, value):
	if key not in dict:
		dict[key] = value

# TODO Ordered by priority:
# Remove NSFW filter to save RAM
# ROCm: https://www.reddit.com/r/StableDiffusion/comments/ww436j/howto_stable_diffusion_on_an_amd_gpu/
# ROCm backup: https://www.gabriel.urdhr.fr/2022/08/28/trying-to-run-stable-diffusion-on-amd-ryzen-5-5600g/
def text2img(pipeline, text: str, **kwargs) -> Image.Image:
	log.info(f"Generating image from '{text}', kwargs: {kwargs}")

	with precision_scope:
		# For info on stable diff args: https://huggingface.co/blog/stable_diffusion
		pipe_out = pipeline(text, **kwargs)
	image: Image.Image = pipe_out.images[0]
	log.info("Image generated")

	# Save tmp image for debugging
	image.save("../data/tmp.png")

	return image

# API function
def generate_image(app_conf: dict, **kwargs) -> bytes:
	# Recover pipeline
	loader_thread: Thread = app_conf.get("pipeline_loader_thread")
	if loader_thread is None:
		raise Exception("Pipeline loader thread not started")
	if loader_thread.is_alive():
		raise ServiceUnavailable("Pipeline loading not finished", retry_after=60*2)
	pipeline = app_conf["pipeline"]

	# Parsing config
	set_default(kwargs, "num_inference_steps", 15)
	set_default(kwargs, "guidance_scale", 7.5)
	set_default(kwargs, "width", 512)
	set_default(kwargs, "height", 512)

	if "text" in kwargs:
		target = kwargs.pop("text")
		target_str = f"\"{target}\""
		f = text2img
	elif "image" in kwargs:
		# TODO support image2image
		target = kwargs.pop("image")
		target_str = f"<Image>"

	# Create progress bar
	request_id = kwargs.pop("request_id")
	port = 8080 # TODO pass ports as docker args
	call_rpc(f"bot:{port}", "pbar_create", request_id, kwargs["num_inference_steps"],
		f"Generating image from {target_str}"
	)

	# Generate image
	image = f(pipeline, target, **kwargs)

	# Encode image to PNG and create response
	im_file = BytesIO()
	image.save(im_file, format="PNG")
	return {
		"image": base64.b64encode(im_file.getvalue()).decode("ascii"),
	}
