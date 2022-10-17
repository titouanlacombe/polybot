import logging, subprocess
from pathlib import Path

log = logging.getLogger(__name__)

dir = Path("../Real-ESRGAN")
model_url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
inputs = dir / "inputs"
outputs = dir / "outputs"
__loaded = False

def load_RealESRGAN():
	global __loaded
	log.info("Loading Real-ESRGAN")

	if __loaded:
		log.info("Real-ESRGAN already loaded")
		return

	log.info("Downloading Real-ESRGAN model")
	subprocess.run(f"cd {dir} && wget {model_url} -P weights -nv", shell=True, check=True)

	__loaded = True
	log.info("Real-ESRGAN loaded")

def _RealESRGAN(input: str, scale: int = 4):
	log.info("Executing Real-ESRGAN")
	subprocess.run(f"python3 {dir}/inference_realesrgan.py -s {scale} --fp32 --ext png -i {input} -o {outputs}", shell=True, check=True)

# Wrapper
def RealESRGAN(input_b: bytes, scale: int = 4) -> bytes:
	if not __loaded:
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
