import os, time
from requests.exceptions import ConnectionError
from diffusers import StableDiffusionPipeline
import torch

device = torch.device(os.getenv("COMPUTE_DEVICE", "cpu"))

# Pipeline kwargs depend on the device
if device.type == "cpu":
	# fp16 not supported on CPU
	# TODO fix on small PC (why expecting bfloat16?)
	kwargs = {}
else:
	# TODO No GPU on WSL => dual boot or use windows
	# https://old.reddit.com/r/StableDiffusion/comments/wv3zam/i_got_stable_diffusion_public_release_working_on/ild7yv3/?context=3
	# Optimization for low VRAM usage
	kwargs = {
		"revision": "fp16",
	}

print("Setting up pipeline, caching pretrained model")
print(f"Device: {device.type}, kwargs: {kwargs}")

while True:
	try:
		pipeline = StableDiffusionPipeline.from_pretrained(
			"CompVis/stable-diffusion-v1-4",
			use_auth_token=os.getenv("HF_TOKEN"),
			cache_dir="../data/hf_cache/models",
			resume_download=True,
			torch_dtype="auto",
			**kwargs
		)
		break
	except ConnectionError as exc:
		print(f"Connection error: {exc}")
		print("Retrying in 2 seconds")
		time.sleep(2)

# From https://github.com/CompVis/stable-diffusion/issues/95
# remove VAE encoder as it's not needed
del pipeline.vae.encoder

print("Pipeline setup complete")
