import logging, requests, os

log = logging.getLogger(__name__)

def call_rpc(host: str, command: str, *args, **kwargs):
	url = f"http://{host}/rpc"
	data = {
		"command": command,
		"args": args,
		"kwargs": kwargs,
	}

	log.info(f"Calling {host}: {data}")
	response: dict = requests.post(url, json=data).json()
	log.info(f"Response from {host}: {response}")
	
	if response.get("error") is not None:
		raise Exception(response["error"])

	return response["result"]

polybot_host = f"bot:{os.environ['POLYBOT_PORT']}"
polybot_api_host = f"bot:{os.environ['POLYBOT_API_PORT']}"
