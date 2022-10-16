import logging, flask
from werkzeug.exceptions import HTTPException

from ImageGenerator import generate_image

log = logging.getLogger(__name__)

app = flask.Flask("ImageGenerator")

rpc_methods = {
	"ping": lambda: "pong",
	"generate": lambda **kwargs: generate_image(app.config, **kwargs),
}

@app.route('/')
def home():
	return "Image generator"

@app.route('/test', methods=["POST"])
def test():
	# curl localhost:5010/test -d "text=<TEXT>"
	rpc_methods["generate"](**flask.request.values.to_dict())
	return "OK"

@app.route('/rpc', methods=['POST'])
def rpc():
	data: dict = flask.request.json

	try:
		res = {
			"result": rpc_methods[data['command']](*data.get("args", []), **data.get("kwargs", {})),
		}
	
	except HTTPException as e:
		log.exception(e)
		raise
	
	except Exception as e:
		log.exception(e)
		res = {
			"error": str(e)
		}

	return flask.jsonify(res)
