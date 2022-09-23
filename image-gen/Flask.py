import json, logging, flask
from werkzeug.exceptions import HTTPException

from ImageGenerator import generate_image

logging.basicConfig(filename="../data/logs/image-gen.log", level=logging.INFO)
log = logging.getLogger(__name__)

app = flask.Flask("ImageGenerator")

rpc_methods = {
	"ping": lambda: "pong",
	"generate": lambda text, **kwargs: generate_image(text, app.config, **kwargs),
}

@app.route('/')
def home():
	return "Image generator"

@app.route('/test', methods=["POST"])
def test():
	text = flask.request.data.decode()
	rpc_methods["generate"](text)
	return "OK"

@app.route('/rpc', methods=['POST'])
def rpc():
	data: dict = flask.request.json

	try:
		res: dict = rpc_methods[data['command']](*data.get("args", []), **data.get("kwargs", {}))
	
	except HTTPException:
		raise
	
	except Exception as e:
		log.exception(e)
		res = {
			"error": str(e)
		}

	return json.dumps(res)
