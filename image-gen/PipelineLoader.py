import logging, os, time, torch
from requests.exceptions import ConnectionError
from diffusers import StableDiffusionPipeline
from Config import device

log = logging.getLogger(__name__)

def load_pipeline(results: dict):
	log.info("Caching and loading pretrained pipeline")
	log.info(f"Device: {device.type}")

	while True:
		try:
			pipeline = StableDiffusionPipeline.from_pretrained(
				"CompVis/stable-diffusion-v1-4",
				
				# CPU does not support half precision optimizations
				revision = "fp16" if device.type == "cuda" else None,
				torch_dtype = torch.float16 if device.type == "cuda" else None,

				use_auth_token=os.getenv("HF_TOKEN"),
				cache_dir="../data/hf_cache/models",
				device=device,
				resume_download=True,
			)
			break
		except ConnectionError as exc:
			log.info(f"Connection error: {exc}")
			log.info("Retrying in 2 seconds")
			time.sleep(2)
	
	log.info("Pipeline loading complete")

	# From https://github.com/CompVis/stable-diffusion/issues/95
	# remove VAE encoder as it's not needed
	del pipeline.vae.encoder

	# TODO Do i need these lines (do device=device work)?
	# if device.type != "cpu":
	# 	pipeline.to(device)

	results["pipeline"] = pipeline
