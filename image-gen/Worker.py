import logging, signal, threading, torch, asyncio
logging.basicConfig(
	filename="../data/logs/image-gen.log",
	level=logging.INFO,
	format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s",
	datefmt="%Y-%m-%d %H:%M:%S",
)

from Flask import app
from Config import device
from PipelineLoader import load_pipeline

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
thread = threading.Thread(target=load_pipeline, args=(app.config,), daemon=True)
thread.start()
app.config["pipeline_loader_thread"] = thread

# Start a event loop daemon thread
event_loop = asyncio.new_event_loop()
thread = threading.Thread(target=event_loop.run_forever, daemon=True)
thread.start()
app.config["event_loop"] = event_loop

app.logger.info("Worker started")
