import logging, base64, threading, torch
from pathlib import Path
from io import BytesIO
from werkzeug.exceptions import ServiceUnavailable
from PIL import Image

from Config import precision_scope
from Microservices import call_rpc, polybot_api_host

log = logging.getLogger(__name__)
jobs_sem = threading.Semaphore(1)
archive_dir = Path("../data/generated_images")
archive_dir.mkdir(parents=True, exist_ok=True)

def constrain(dict, key, min, max, default):
	if key not in dict:
		dict[key] = default

	if dict[key] < min:
		raise Exception(f"Config '{key}' < {min}")

	if dict[key] > max:
		raise Exception(f"Config '{key}' > {max}")

def estimate_eta(image_size: int, num_inference_steps: int):
	base_size = 512 * 512
	base_time = 10 # seconds per inference step on 512x512 image
	return base_time * (image_size / base_size) * num_inference_steps

def text2img(pipeline, text: str, **kwargs) -> Image.Image:
	log.info(f"Generating image from '{text}', kwargs: {kwargs}")

	with torch.no_grad():
		with precision_scope:
			# For info on stable diff args: https://huggingface.co/blog/stable_diffusion
			pipe_out = pipeline(text, **kwargs)

	image: Image.Image = pipe_out.images[0]
	log.info("Image generated")

	return image

def _generate_image(app_conf: dict, **kwargs) -> bytes:
	pipeline = app_conf["pipeline"]

	log.info(f"Parsing config: {kwargs}")
	constrain(kwargs, "num_inference_steps", 1, 50, 15)
	constrain(kwargs, "guidance_scale", 0, 10, 7.5)
	constrain(kwargs, "width", 8, 512, 512)
	constrain(kwargs, "height", 8, 512, 512)
	request_id = kwargs.pop("request_id", None)

	if "text" in kwargs:
		input = kwargs.pop("text")
		steps = kwargs["num_inference_steps"]
		op = text2img
	elif "image_url" in kwargs:
		# TODO support image2image
		raise Exception("Image2image not implemented")
		input = kwargs.pop("image_url")
		steps = 1
		op = lambda *args, **kwargs: Image.new("RGB", (512, 512))

	# Create progress bar
	if request_id is not None:
		call_rpc(polybot_api_host, "pbar_create", request_id, steps,
			f"Generating image from '{input}', ETA: {int(estimate_eta(kwargs['width'] * kwargs['height'], steps))} s"
		)

	try:
		# Generate image
		image = op(pipeline, input, **kwargs)

		# Encode image to PNG and create response
		im_file = BytesIO()
		image.save(im_file, format="PNG")

		# Save image bytes to archive
		safe_name = "".join(c for c in input if c.isalnum() or c in " _-")
		safe_name = safe_name[:64]
		with open(archive_dir / f"{safe_name}.png", "wb") as f:
			f.write(im_file.getvalue())
	
	finally:
		# Delete progress bar
		if request_id is not None:
			call_rpc(polybot_api_host, "pbar_finish", request_id)

	return {
		"image": base64.b64encode(im_file.getvalue()).decode(),
	}

# API function
def generate_image(app_conf: dict, **kwargs) -> bytes:
	# Pre conditions
	loader_thread: threading.Thread = app_conf.get("pipeline_loader_thread")
	if loader_thread is None:
		raise Exception("Pipeline loader thread not started")
	if loader_thread.is_alive():
		raise ServiceUnavailable("Pipeline loading not finished", retry_after=60*2)

	if not jobs_sem.acquire(blocking=False):
		raise ServiceUnavailable("Too many jobs currently running", retry_after=60*2)

	try:
		return _generate_image(app_conf, **kwargs)
	finally:
		jobs_sem.release()
	