import logging, base64, threading, torch, time
from pathlib import Path
from io import BytesIO
from werkzeug.exceptions import ServiceUnavailable
from PIL import Image

from Config import precision_scope
from Utils import constrain, null_func
from Text2Img import text2img
from Microservices import call_rpc, polybot_api_host

log = logging.getLogger(__name__)
job_sem = threading.Semaphore(1)

archive_dir = Path("../data/generated_images")
archive_dir.mkdir(parents=True, exist_ok=True)

def _generate_image(app_conf: dict, **kwargs) -> bytes:
	log.info(f"Parsing config: {kwargs}")
	constrain(kwargs, "num_inference_steps", 1, 50, 15)
	constrain(kwargs, "guidance_scale", 0, 10, 7.5)
	constrain(kwargs, "width", 8, 512, 512)
	constrain(kwargs, "height", 8, 512, 512)
	kwargs["pipeline"] = app_conf["pipeline"]

	# Parsing operation
	if "prompt" in kwargs:
		name = kwargs["prompt"]
		pbar_steps = kwargs["num_inference_steps"] + 2
		op = text2img
	elif "image_url" in kwargs:
		# TODO support image2image
		raise Exception("Image2image not implemented")
		name = kwargs["image_url"]
		pbar_steps = 1
		op = null_func
	else:
		raise Exception("No input specified")

	# Parsing pbar params
	request_id = kwargs.pop("request_id", None)
	kwargs["step_callback"] = null_func if request_id is None else lambda step, latents: call_rpc(polybot_api_host, "pbar_update", request_id, step)

	# Create pbar
	if request_id is not None:
		call_rpc(polybot_api_host, "pbar_create", request_id, pbar_steps, f"Generating image '{name}'")

	try:
		log.info(f"Generating image '{name}'")
		t = time.time()

		with torch.inference_mode(), precision_scope:
			image: Image.Image = op(**kwargs)

		log.info(f"Generated image '{name}' in {time.time() - t:.2f}s")

	finally:
		# Delete progress bar
		if request_id is not None:
			call_rpc(polybot_api_host, "pbar_finish", request_id)

	# Encode image to PNG and create response
	im_file = BytesIO()
	image.save(im_file, format="PNG")

	# Save image bytes to archive
	safe_name = "".join(c for c in name if c.isalnum() or c in " _-")
	if len(safe_name) > 64:
		safe_name = safe_name[:64] + "..."
	with open(archive_dir / f"{safe_name}.png", "wb") as f:
		f.write(im_file.getvalue())

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

	if not job_sem.acquire(blocking=False):
		raise ServiceUnavailable("Too many jobs currently running", retry_after=60*2)

	try:
		return _generate_image(app_conf, **kwargs)
	finally:
		job_sem.release()
