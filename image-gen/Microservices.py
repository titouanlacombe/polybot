import logging, requests

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
