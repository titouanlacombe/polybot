import json, logging, flask
from ImageGenerator import text2img

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
	data = flask.request.json

	try:
		res = rpc_methods[data['command']](*data['args'], **data['kwargs'])
	except Exception as e:
		log.exception(e)
		res = {
			"error": str(e)
		}

	return json.dumps(res)
