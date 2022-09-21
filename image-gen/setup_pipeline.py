import os
from diffusers import StableDiffusionPipeline
import torch

print("Setting up pipeline, caching pretrained model")

pipe = StableDiffusionPipeline.from_pretrained(
	"CompVis/stable-diffusion-v1-4",
	use_auth_token=os.getenv("HF_TOKEN"),
	cache_dir="../data/hf_cache/models",

	# Optimization because i have no RAM :'(
	# TODO how to fix fp16 on the CPU
	revision="fp16",
	torch_dtype=torch.float16,
)

print("Pipeline setup complete")
