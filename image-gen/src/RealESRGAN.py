import logging, os
from pathlib import Path

log = logging.getLogger(__name__)

dir = Path("../data/Real-ESRGAN")
inputs = dir / "inputs"
outputs = dir / "outputs"

def _RealESRGAN(input: str, scale: int = 4):
	log.info("Executing Real-ESRGAN")
	if os.system(f"python3 {dir}/inference_realesrgan.py -s {scale} --fp32 --ext png -i {input} -o {outputs}") != 0:
		raise Exception("Failed to execute Real-ESRGAN")

# Wrapper
def RealESRGAN(input_b: bytes, scale: int = 4) -> bytes:
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
