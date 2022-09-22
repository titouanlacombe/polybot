import os, time, torch
from requests.exceptions import ConnectionError
from diffusers import StableDiffusionPipeline
from huggingface_hub.file_download import hf_hub_download

device = torch.device(os.getenv("COMPUTE_DEVICE", "cpu"))
hf_repo = "CompVis/stable-diffusion-v1-4"
hf_cache = "../data/hf_cache/models"

# fp16 not supported on CPU
# TODO fix on small PC (why expecting bfloat16?)
revision = "main" if device.type == "cpu" else "fp16"

# TODO No GPU on WSL => dual boot or use windows
# https://old.reddit.com/r/StableDiffusion/comments/wv3zam/i_got_stable_diffusion_public_release_working_on/ild7yv3/?context=3
# Optimization for low VRAM usage
torch_dtype = torch.float32 if device.type == "cpu" else torch.float16

if __name__ == "__main__":
	# Download & cache the pipeline without loading
	print("Caching pretrained pipeline")
	print(f"Device: {device.type}, revision: {revision}, torch_dtype: {torch_dtype}")

	while True:
		try:
			hf_hub_download(
				repo_id=hf_repo,
				revision=revision,
				filename="config.json",
				cache_dir=hf_cache,
				resume_download=True,
				use_auth_token=os.getenv("HF_TOKEN"),
			)
			break
		except ConnectionError as exc:
			print(f"Connection error: {exc}")
			print("Retrying in 2 seconds")
			time.sleep(2)
	
	print("Pipeline caching complete")
	exit(0)

def load_pipeline():
	pipeline = StableDiffusionPipeline.from_pretrained(
		hf_repo,
		cache_dir=hf_cache,
		torch_dtype=torch_dtype,
		revision=revision,
		device=device,
		local_files_only=True,
	)

	# From https://github.com/CompVis/stable-diffusion/issues/95
	# remove VAE encoder as it's not needed
	del pipeline.vae.encoder

	if device.type != "cpu":
		pipeline.to(device)

	return pipeline
