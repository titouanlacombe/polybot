import logging
logging.basicConfig(filename="../data/logs/image-gen.log", level=logging.INFO)

import threading
from Flask import app
from PipelineLoader import load_pipeline

# Start a daemon thread to load the pipeline
thread = threading.Thread(target=load_pipeline, args=(app.config,), daemon=True)
thread.start()

app.config["pipeline_loader_thread"] = thread

app.logger.info("Worker started")
