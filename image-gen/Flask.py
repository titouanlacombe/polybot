import json, logging, flask
from werkzeug.exceptions import HTTPException

from ImageGenerator import generate_image

logging.basicConfig(filename="../data/logs/image-gen.log", level=logging.INFO)
log = logging.getLogger(__name__)

app = flask.Flask("ImageGenerator")

rpc_methods = {
	"ping": lambda: "pong",
	"generate": lambda **kwargs: generate_image(app.config, **kwargs),
}

@app.route('/')
def home():
	return "Image generator"

# TODO search {'trained_betas'} was not found in config. Values will be initialized to default values.
@app.route('/test', methods=["POST"])
def test():
	# curl localhost:5010/test -d "text=<TEXT>"
	rpc_methods["generate"](**flask.request.values.to_dict())
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
