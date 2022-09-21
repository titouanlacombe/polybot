import os
from diffusers import StableDiffusionPipeline
import torch

device = torch.device(os.getenv("COMPUTE_DEVICE", "cpu"))

if device.type == "cuda":
	# Optimization because i have no RAM :'(
	kwargs = {
		"revision": "fp16",
		"torch_dtype": torch.float16
	}
elif device.type == "rocm":
	kwargs = {
		"revision": "fp16",
		"torch_dtype": torch.float16
	}
else:
	# CPU or unknown device
	# TODO fix fp16 on the CPU (test)
	kwargs = {
		"revision": "fp16",
		"torch_dtype": torch.float16
	}

print("Setting up pipeline, caching pretrained model")

pipeline = StableDiffusionPipeline.from_pretrained(
	"CompVis/stable-diffusion-v1-4",
	use_auth_token=os.getenv("HF_TOKEN"),
	cache_dir="../data/hf_cache/models",
	resume_download=True,
	**kwargs
)

# From https://github.com/CompVis/stable-diffusion/issues/95
# remove VAE encoder as it's not needed
del pipeline.vae.encoder

print("Pipeline setup complete")
