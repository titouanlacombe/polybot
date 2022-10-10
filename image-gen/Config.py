import logging, os, torch, types

log = logging.getLogger(__name__)

# ROCm and CUDA falls under device type "cuda"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# My CPU does not support half precision optimizations
precision_scope = torch.autocast(device.type) if device.type == "cuda" else torch.no_grad()

cpu_count = os.cpu_count()
torch.set_num_threads(cpu_count)
torch.set_num_interop_threads(cpu_count)

# Logging configuration
def is_variable(obj):
	return not callable(obj) and not isinstance(obj, (types.ModuleType, type))
vars = {k: v for k, v in locals().items() if not k.startswith("__") and is_variable(v)}
log.info(f"Config: {vars}")
