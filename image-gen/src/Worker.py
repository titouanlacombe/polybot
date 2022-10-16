import logging, signal, threading, torch, asyncio
logging.basicConfig(
	filename="../data/logs/image-gen.log",
	level=logging.INFO,
	format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
)

from Flask import app
from Config import device
from StableDiffusion import load_SD
from RealESRGAN import load_RealESRGAN

def close(signum, frame):
	app.logger.info(f"Received signal {signum}, exiting")
	
	if app.config.get("pipeline") is not None:
		del app.config["pipeline"]

	if device.type != "cpu":
		torch.cuda.empty_cache()
	
	app.logger.info("Worker stopped")
	exit(0)

signal.signal(signal.SIGTERM, close)
signal.signal(signal.SIGINT, close)
signal.signal(signal.SIGQUIT, close)
signal.signal(signal.SIGABRT, close)

def log_segfault(signum, frame):
	logging.error("Segmentation fault")
	exit(1)

signal.signal(signal.SIGSEGV, log_segfault)

# Start a daemon thread to load the pipeline
threading.Thread(target=load_SD, args=(app.config,), daemon=True).start()

# Start a event loop daemon thread
event_loop = asyncio.new_event_loop()
app.config["event_loop"] = event_loop
threading.Thread(target=event_loop.run_forever, daemon=True).start()

# Load Real-ESRGAN
threading.Thread(target=load_RealESRGAN, args=(app.config,), daemon=True).start()

app.logger.info("Worker started")
