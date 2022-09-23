import logging, os, torch

log = logging.getLogger(__name__)

# ROCm and CUDA falls under device type "cuda"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# My CPU does not support half precision optimizations
precision_scope = torch.autocast(device.type) if device.type == "cuda" else torch.no_grad()

torch.set_num_threads(os.cpu_count())
torch.set_num_interop_threads(os.cpu_count())

log.info(f"Image-gen config: device={device}, precision_scope={precision_scope}, num_threads={torch.get_num_threads()}, num_interop_threads={torch.get_num_interop_threads()}")
