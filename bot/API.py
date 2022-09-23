import json, logging, flask, socket, sentry_sdk
import Config.App as App
import Utils.Sentry as Sentry
from sentry_sdk.integrations.flask import FlaskIntegration

log = logging.getLogger(__name__)

app = flask.Flask(__name__)
Sentry.init([FlaskIntegration()])

def socket_send(host: str, port: int, data: str, buffer=1024*4):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((host, port))
		# Send data length
		s.sendall(len(data).to_bytes(4, "big"))
		# Send data
		s.sendall(data.encode())
		return s.recv(buffer).decode()
	finally:
		s.close()

@app.route('/')
def home():
	return flask.render_template("web-remote.html", env_color=App.env_color)

@app.route('/ping')
def ping():
	return "pong"

@app.route('/rpc', methods=['POST'])
def rpc():
	data: dict = flask.request.json
	log.info(f"Received RPC: {data}")

	try:
		# Call polybot rpc
		res = socket_send("localhost", int(App.polybot_port), json.dumps(data))
		res = json.loads(res)
	except Exception as exc:
		log.exception(exc)
		sentry_sdk.capture_exception(exc)
		res = {
			"error": str(exc)
		}

	return flask.jsonify(res)
