import logging
logging.basicConfig(filename="../data/logs/image-gen.log", level=logging.INFO)

import signal, threading, torch

from Flask import app
from Config import device
from PipelineLoader import load_pipeline

def close(signum, frame):
	app.logger.info("Stopping worker")
	
	if app.config["pipeline"] is not None:
		del app.config["pipeline"]

	if device.type != "cpu":
		torch.cuda.empty_cache()
	
	app.logger.info("Worker stopped")
	exit(0)

signal.signal(signal.SIGTERM, close)

# Start a daemon thread to load the pipeline
thread = threading.Thread(target=load_pipeline, args=(app.config,), daemon=True)
thread.start()

app.config["pipeline_loader_thread"] = thread

app.logger.info("Worker started")
