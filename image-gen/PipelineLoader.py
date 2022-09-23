import logging, os, time, torch
from requests.exceptions import ConnectionError
from diffusers import StableDiffusionPipeline
from Config import device

log = logging.getLogger(__name__)

def load_pipeline(results: dict):
	start = time.time()
	
	log.info("Caching and loading pretrained pipeline")

	while True:
		try:
			pipeline = StableDiffusionPipeline.from_pretrained(
				"CompVis/stable-diffusion-v1-4",
				
				# CPU does not support half precision optimizations
				revision = "fp16" if device.type == "cuda" else None,
				torch_dtype = torch.float16 if device.type == "cuda" else None,

				use_auth_token=os.getenv("HF_TOKEN"),
				cache_dir="../data/hf_cache/models",
				# device=device,
				resume_download=True,
			)
			break
		except ConnectionError as exc:
			log.info(f"Connection error: {exc}")
			log.info("Retrying in 2 seconds")
			time.sleep(2)

	# TODO Create own pipeline to avoid this (packages/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion.py)
	# Remove VAE encoder as it's only needed for training (https://huggingface.co/blog/stable_diffusion)
	del pipeline.vae.encoder

	# Remove NSFW filter to save RAM
	def feature_extractor_dummy(image, **kwargs):
		t = torch.Tensor()
		t.pixel_values = None
		return t
	pipeline.feature_extractor = feature_extractor_dummy
	pipeline.safety_checker = lambda images, **kwargs: (images, False)

	if device.type != "cpu":
		pipeline.to(device)

	results["pipeline"] = pipeline
	
	t = time.time() - start
	log.info(f"Pipeline loaded in {t:.2f} s")
