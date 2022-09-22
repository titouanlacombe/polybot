import json, logging, flask, base64
from threading import Thread
from werkzeug.exceptions import ServiceUnavailable, HTTPException
from ImageGenerator import text2img

logging.basicConfig(filename="../data/logs/image-gen.log", level=logging.INFO)
log = logging.getLogger(__name__)

app = flask.Flask("ImageGenerator")

def generate_image(text: str, **kwargs) -> bytes:
	loader_thread: Thread = app.config.get("pipeline_loader_thread")

	if loader_thread is None:
		raise Exception("Pipeline loader thread not started")

	if loader_thread.is_alive():
		raise ServiceUnavailable("Pipeline loading in progress", retry_after=60*2)

	# Recover thread result
	pipeline = app.config["pipeline"]

	return text2img(pipeline, text, **kwargs)

rpc_methods = {
	"ping": lambda: "pong",
	"generate": generate_image,
}

@app.route('/')
def home():
	return "Image generator"

@app.route('/test', methods=["POST"])
def test():
	text = flask.request.data.decode()
	generate_image(text)
	return "OK"

@app.route('/rpc', methods=['POST'])
def rpc():
	data: dict = flask.request.json

	try:
		image_data: bytes = rpc_methods[data['command']](*data.get("args", []), **data.get("kwargs", {}))
		res = {
			"image_data": base64.b64encode(image_data).decode("ascii"),
		}
	except HTTPException:
		raise
	
	except Exception as e:
		log.exception(e)
		res = {
			"error": str(e)
		}

	return json.dumps(res)
