import os
from diffusers import StableDiffusionPipeline
import torch

compute_device = os.getenv("COMPUTE_DEVICE", "cpu")

# TODO how to fix fp16 on the CPU
if compute_device == "cpu":
	device = torch.device("cpu")
	kwargs = {
		"revision": "fp16",
		"torch_dtype": torch.bfloat16
	}
elif compute_device == "cuda":
	device = torch.device("cuda")
	# Optimization because i have no RAM :'(
	kwargs = {
		"revision": "fp16",
		"torch_dtype": torch.float16
	}
elif compute_device == "rocm":
	device = torch.device("rocm")
	kwargs = {
		"revision": "fp16",
		"torch_dtype": torch.float16
	}
else:
	raise Exception(f"Unknown compute_device: {compute_device}")

print("Setting up pipeline, caching pretrained model")

pipe = StableDiffusionPipeline.from_pretrained(
	"CompVis/stable-diffusion-v1-4",
	use_auth_token=os.getenv("HF_TOKEN"),
	cache_dir="../data/hf_cache/models",
	**kwargs
)

print("Pipeline setup complete")
