import json, logging, flask, socket

import config.App as App

log = logging.getLogger(__name__)

app = flask.Flask(__name__)

def socket_send(host: str, port: int, data: str, buffer=1024*4):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))

		# Send data length, then data
		s.send(len(data).to_bytes(4, "big"))
		s.sendall(data.encode())

		# Read response until EOF
		resp = b""
		while True:
			data = s.recv(buffer)
			if not data:
				break
			resp += data

		return resp.decode()
	finally:
		s.close()

@app.route('/')
def home():
	return flask.render_template("web-remote.jinja", env_color=App.env_color)

@app.route('/resources/<path:path>')
def resources(path):
	return flask.send_from_directory("../data/resources", path)

@app.route('/ping')
def ping():
	return "pong"

@app.route('/rpc', methods=['POST'])
def rpc():
	data: dict = flask.request.json
	log.info(f"RPC query: {data}")

	# Call polybot rpc
	try:
		res = socket_send(App.polybot_host, App.polybot_port, json.dumps(data))
		log.info(f"RPC response: {res}")
		res = json.loads(res)
	except Exception as exc:
		log.exception(exc)
		res = {
			"error": str(exc)
		}

	return flask.jsonify(res)
