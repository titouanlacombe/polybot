import logging, os
from pathlib import Path

log = logging.getLogger(__name__)

dir = Path("../Real-ESRGAN")
model_url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
inputs = dir / "inputs"
outputs = dir / "outputs"

def load_RealESRGAN(config: dict):
	log.info("Loading Real-ESRGAN")

	# If no model in wheights, download it
	if len(list((dir/"weights").glob("*.pth"))) == 0:
		log.info("Downloading Real-ESRGAN model")
		os.system(f"cd {dir} && wget {model_url} -P weights -nv")

	config["RealESRGAN_loaded"] = True
	log.info("Real-ESRGAN loaded")

def _RealESRGAN(input: str, scale: int = 4):
	log.info("Executing Real-ESRGAN")
	if os.system(f"python3 {dir}/inference_realesrgan.py -s {scale} --fp32 --ext png -i {input} -o {outputs}") != 0:
		raise Exception("Failed to execute Real-ESRGAN")

# Wrapper
def RealESRGAN(config: dict, input_b: bytes, scale: int = 4) -> bytes:
	if not config.get("RealESRGAN_loaded"):
		raise Exception("Real-ESRGAN not loaded")
		
	input: Path = inputs / "tmp.png"
	output: Path = outputs / "tmp_out.png"

	try:
		input.write_bytes(input_b)
		_RealESRGAN(input, scale)

		with open(output, "rb") as f:
			return f.read()

	finally:
		input.unlink()
		output.unlink()
