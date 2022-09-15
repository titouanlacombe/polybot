import logging, time, uuid, flask

def register_io_logging(app: flask.Flask):
	# IO request log
	@app.before_request
	def log_request_info():
		flask.request.start_time = time.time()
		flask.request.log = logging.getLogger(str(uuid.uuid4())[:8])
		flask.request.log.info(f"[{flask.request.method}] on '{flask.request.url}'")

	@app.after_request
	def after_request(response):
		t = round((time.time() - flask.request.start_time) * 1000)
		flask.request.log.info(f"Responded {response.status} in {t} ms")
		return response
