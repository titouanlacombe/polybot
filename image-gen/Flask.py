import json, logging, flask, base64
from ImageGenerator import text2img

logging.basicConfig(filename="../data/logs/image-gen.log", level=logging.INFO)
log = logging.getLogger(__name__)
app = flask.Flask(__name__)

rpc_methods = {
	"ping": lambda: "pong",
	"generate": text2img,
}

@app.route('/')
def home():
	return "Image generator"

@app.route('/rpc', methods=['POST'])
def rpc():
	data: dict = flask.request.json

	try:
		image_data: bytes = rpc_methods[data['command']](*data.get("args", []), **data.get("kwargs", {}))
		res = {
			"image_data": base64.b64encode(image_data).decode("ascii"),
		}
	except Exception as e:
		log.exception(e)
		res = {
			"error": str(e)
		}

	return json.dumps(res)

log.info("Worker started")
