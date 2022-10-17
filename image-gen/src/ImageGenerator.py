import logging, threading, torch, time
from pathlib import Path
from io import BytesIO
from werkzeug.exceptions import ServiceUnavailable
from PIL import Image

from Config import precision_scope
from Utils import constrain, null_func
from Text2Img import text2img
from Microservices import call_rpc, call_rpc_no_wait, polybot_api_host
from RealESRGAN import RealESRGAN

log = logging.getLogger(__name__)
job_sem = threading.Semaphore(1)

archive_dir = Path("../data/generated_images")
archive_dir.mkdir(parents=True, exist_ok=True)

def get_safe_name(text: str) -> str:
	safe_name = "".join(c for c in text if c.isalnum() or c in " _-")
	if len(safe_name) > 64:
		safe_name = safe_name[:64] + "..."
	return safe_name

def pipeline(**kwargs):
	log.info(f"Generating image")
	t = time.time()

	with torch.inference_mode(), precision_scope:
		image: Image.Image = text2img(**kwargs)

	# Upscale using Real-ESRGAN
	mem_file = BytesIO()
	image.save(mem_file, format="PNG", quality=100)
	upscaled_bytes = RealESRGAN(mem_file.getvalue(), 2)
	image = Image.open(BytesIO(upscaled_bytes))

	# Save image to archives
	path = archive_dir / f"{get_safe_name(kwargs['prompt'])}.jpeg"
	image.save(path, quality=75, optimize=True, progressive=True)

	log.info(f"Generated image in {time.time() - t:.2f}s")

	return path

def pbar_wrapper(event_loop, op, **kwargs):
	# Update progress bar callback
	request_id = kwargs.pop("request_id", None)
	def update_pbar(step, latents):
		call_rpc_no_wait(event_loop, polybot_api_host, "pbar_update", request_id, step)
	kwargs["step_callback"] = update_pbar if request_id else null_func

	# Create progress bar
	if request_id is not None:
		call_rpc(polybot_api_host, "pbar_create", request_id, kwargs["num_inference_steps"], f"Generating image")

	try:
		return op(**kwargs)
	finally:
		# Finish progress bar
		if request_id is not None:
			call_rpc(event_loop, polybot_api_host, "pbar_finish", request_id)

# API function
def generate_image(app_conf: dict, **kwargs):
	if app_conf.get("pipeline") is None:
		raise ServiceUnavailable("Pipeline loading not finished", retry_after=60*2)

	constrain(kwargs, "num_inference_steps", 1, 50, 15)
	constrain(kwargs, "guidance_scale", 0, 10, 7.5)
	constrain(kwargs, "width", 8, 512, 512)
	constrain(kwargs, "height", 8, 512, 512)
	kwargs["pipeline"] = app_conf["pipeline"]

	if not job_sem.acquire(blocking=False):
		raise ServiceUnavailable("Too many jobs currently running", retry_after=60*2)

	try:
		return pbar_wrapper(app_conf["event_loop"], pipeline, **kwargs)
	finally:
		job_sem.release()
