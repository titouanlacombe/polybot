import asyncio, logging, aiohttp, os

log = logging.getLogger(__name__)

session = aiohttp.ClientSession()

async def async_call_rpc(host: str, command: str, *args, **kwargs):
	data = {
		"command": command,
		"args": args,
		"kwargs": kwargs,
	}

	log.info(f"Calling {host}: {data}")

	async with session.post(f"http://{host}/rpc", json=data) as resp:
		if resp.status < 200 or resp.status >= 300:
			raise Exception(f"RPC failed with status {resp.status}: {await resp.text()}")
		
		response: dict = await resp.json()
		log.info(f"Response from {host}: {response}")
	
	if response.get("error") is not None:
		raise Exception(response["error"])

	return response["result"]

def call_rpc(host: str, command: str, *args, **kwargs):
	return asyncio.run(async_call_rpc(host, command, *args, **kwargs))

polybot_host = f"bot:{os.environ['POLYBOT_PORT']}"
polybot_api_host = f"bot:{os.environ['POLYBOT_API_PORT']}"
