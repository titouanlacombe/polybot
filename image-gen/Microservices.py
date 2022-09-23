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
	response = requests.post(url, json=data)
	log.info(f"Response from {host}: {response}")
	
	return response.json()

polybot_host = f"bot:{os.environ['POLYBOT_PORT']}"
polybot_api_host = f"bot:{os.environ['POLYBOT_API_PORT']}"
