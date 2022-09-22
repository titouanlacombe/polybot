import torch

# ROCm and CUDA falls under device type "cuda"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# My CPU does not support half precision optimizations
precision_scope = torch.autocast(device.type) if device.type == "cuda" else torch.no_grad()
