import logging, subprocess
from pathlib import Path

log = logging.getLogger(__name__)

esrgan_src = Path("../Real-ESRGAN")
esrgan_data = Path("../data") / "real-esrgan"
inputs = esrgan_data / "inputs"
outputs = esrgan_data / "outputs"
model_cache = esrgan_data / "RealESRGAN_x4plus_cache.pth"
model_url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"

__loaded = False

def load_RealESRGAN():
	global __loaded
	log.info("Loading Real-ESRGAN")

	# If model is not downloaded, download it
	if not model_cache.exists():
		log.info("Downloading Real-ESRGAN model")
		model_cache.parent.mkdir(parents=True, exist_ok=True)
		subprocess.run(f"curl {model_url} > {model_cache}", shell=True, check=True)

	__loaded = True
	log.info("Real-ESRGAN loaded")

def _RealESRGAN(inputs: str, scale: int = 4):
	log.info("Executing Real-ESRGAN")
	subprocess.run(f"python3 {esrgan_src}/inference_realesrgan.py -s {scale} --fp32 --ext png -i {inputs} -o {outputs} --model_path {model_cache}", shell=True, check=True)

# Wrapper
def RealESRGAN(input_b: bytes, scale: int = 4) -> bytes:
	if not __loaded:
		raise Exception("Real-ESRGAN not loaded")
		
	input: Path = inputs / "tmp.png"
	output: Path = outputs / "tmp_out.png"

	try:
		input.write_bytes(input_b)

		_RealESRGAN(inputs, scale)

		with open(output, "rb") as f:
			return f.read()

	finally:
		input.unlink()
		output.unlink()
