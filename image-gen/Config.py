import os, torch

device = torch.device(os.getenv("COMPUTE_DEVICE", "cpu"))

# fp16 not supported on CPU
# TODO fix on small PC (why expecting bfloat16?)
revision = "main" if device.type == "cpu" else "fp16"

# TODO No GPU on WSL => dual boot or use windows
# https://old.reddit.com/r/StableDiffusion/comments/wv3zam/i_got_stable_diffusion_public_release_working_on/ild7yv3/?context=3
# Optimization for low VRAM usage
torch_dtype = torch.float32 if device.type == "cpu" else torch.float16
