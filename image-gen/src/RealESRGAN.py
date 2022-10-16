import logging, os, tempfile

log = logging.getLogger(__name__)

url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip"
outpath = "../data/RealESRGAN"
exec = "realesrgan-ncnn-vulkan"

def load_RealESRGAN(config: dict):
	if os.path.exists(outpath):
		log.info("Real-ESRGAN cache found")
		config["RealESRGAN"] = outpath
		return

	log.info("Downloading Real-ESRGAN")
	if os.system(f"wget {url} -O {outpath}.zip -nv") != 0:
		raise Exception("Failed to download Real-ESRGAN")
	
	log.info("Exctracting Real-ESRGAN")
	if os.system(f"unzip {outpath}.zip -d {outpath}") != 0:
		raise Exception("Failed to extract Real-ESRGAN")
	os.system(f"rm {outpath}.zip")

	# Adding user execution rights
	os.system(f"chmod u+x {outpath}/{exec}")

	log.info("Real-ESRGAN loaded")
	config["RealESRGAN"] = outpath

def _RealESRGAN(config: dict, input: str, output: str, scale: int = 4):
	if config.get("RealESRGAN") is None:
		raise Exception("Real-ESRGAN not loaded")

	log.info("Executing Real-ESRGAN")
	if os.system(f"{config['RealESRGAN']}/{exec} -i {input} -o {output} -s {scale}") != 0:
		raise Exception("Failed to execute Real-ESRGAN")

# Wrapper
def RealESRGAN(config: dict, input: bytes, scale: int = 4) -> bytes:
	input_f = tempfile.NamedTemporaryFile(suffix=".png")
	output_f = tempfile.NamedTemporaryFile(suffix=".png")
	input_f.write(input)

	_RealESRGAN(config, input_f.name, output_f.name, scale)

	output_f.seek(0)
	return output_f.read()
