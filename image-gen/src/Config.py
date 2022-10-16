import logging, os, torch, types
from contextlib import nullcontext

log = logging.getLogger(__name__)

# ROCm and CUDA falls under device type "cuda"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# CPU does not support half precision optimizations
use_half_model = device.type == "cuda"

if device.type == "cpu":
	# CPU does not support half precision optimizations
	precision_scope = nullcontext()
else:
	if use_half_model:
		# Stable diffusion is faster on half model when autocast is disabled (https://github.com/huggingface/diffusers/pull/511)
		precision_scope = nullcontext()
	else:
		# Enable autocast for faster inference on GPU
		precision_scope = torch.autocast(device.type)

cpu_count = os.cpu_count()
torch.set_num_threads(cpu_count)
torch.set_num_interop_threads(cpu_count)

# Log configuration
def is_variable(obj):
	return not callable(obj) and not isinstance(obj, (types.ModuleType, type))
vars = {k: v for k, v in locals().items() if not k.startswith("__") and is_variable(v)}
log.info(f"Config: {vars}")
