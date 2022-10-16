import asyncio, logging, aiohttp, os

log = logging.getLogger(__name__)

async def async_call_rpc(host: str, command: str, *args, **kwargs):
	data = {
		"command": command,
		"args": args,
		"kwargs": kwargs,
	}

	log.info(f"Calling {host}: {data}")

	async with aiohttp.ClientSession() as session:
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

# Call rpc without waiting for response
def call_rpc_no_wait(event_loop: asyncio.AbstractEventLoop, host: str, command: str, *args, **kwargs):
	asyncio.run_coroutine_threadsafe(async_call_rpc(host, command, *args, **kwargs), event_loop)

polybot_host = f"bot:{os.environ['POLYBOT_PORT']}"
polybot_api_host = f"bot:{os.environ['POLYBOT_API_PORT']}"
