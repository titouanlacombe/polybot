import logging, os, tempfile

log = logging.getLogger(__name__)

url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip"
outpath = "../data/RealESRGAN"

def load_RealESRGAN(config: dict):
	if os.path.exists(outpath):
		log.info("Real-ESRGAN cache found")
		config["RealESRGAN"] = outpath
		return

	log.info("Downloading Real-ESRGAN")
	os.system(f"wget {url} -O {outpath}.zip")
	
	log.info("Exctracting Real-ESRGAN")
	os.system(f"unzip {outpath}.zip -d {outpath}")
	os.system(f"rm {outpath}.zip")

	log.info("Real-ESRGAN loaded")
	config["RealESRGAN"] = outpath

def _RealESRGAN(config: dict, input: str, output: str, scale: int = 4):
	if config.get("RealESRGAN") is None:
		raise Exception("Real-ESRGAN not loaded")

	log.info("Executing Real-ESRGAN")
	os.system(f"{config['RealESRGAN']}/realesrgan-ncnn-vulkan -i {input} -o {output} -s {scale}")

# Wrapper
def RealESRGAN(config: dict, input: bytes, scale: int = 4) -> bytes:
	input_f = tempfile.NamedTemporaryFile(suffix=".png")
	output_f = tempfile.NamedTemporaryFile(suffix=".png")
	input_f.write(input)

	_RealESRGAN(config, input_f.name, output_f.name, scale)

	output_f.seek(0)
	return output_f.read()
