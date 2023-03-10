import asyncio, logging, base64, yaml, math, random, discord, aiohttp, json
from time import time as time_now
from io import BytesIO
from datetime import datetime, date, time, timedelta
from discord.ext.commands import Context

from Message2Images import message2images
from TimeToSuffer import gettimetosuffer, endofformation, endofday, gettimetosuffer_ofuser
import config.App as App
import config.Users as Users
from PolyBot import PolyBot
from PolyQuiz import do_quiz

random.seed()
log = logging.getLogger(__name__)

image_gen_help = f"""
Usage:
Prompt mode: \"{App.command_prefix}imagen <prompt>\"

Preset mode: \"{App.command_prefix}imagen #<preset> <prompt>\"

YAML mode: \"{App.command_prefix}imagen
prompt: '<prompt>'
gen:
  generator_option: value
upscale:
  upscaler_option: value
\"

Available options:
Generator:
- prompt: input prompt
- iter: higher quality but slower (default: 50)
- guidance: how much should the result be guided by the prompt at the cost of quality (default: 6)
- w: result image width (default: 512)
- h: result image height (default: 512)
Upscaler:
- iter: higher quality but slower (default: 30)
- guidance: how much should the result be guided by the prompt at the cost of quality (default: 2)
""".strip()

imagen_presets = {
	"low": {
		"gen": {
			"iter": 30,
			"guidance": 5,
		},
		"upscale": {
			"skip": True,
		},
	},
	"high": {
		"gen": {
			"iter": 60,
			"guidance": 7,
		},
		"upscale": {
			"iter": 40,
		},
	},
	"ultra": {
		"gen": {
			"iter": 60,
			"guidance": 7,
            "w": 768,
            "h": 768,
		},
		"upscale": {
			"iter": 40,
		},
	},
}

def get_imagen_options(message: str):
	# YAML mode
	try:
		decoded = yaml.safe_load(message)
		if not isinstance(decoded, dict):
			raise ValueError("Invalid YAML")
		return decoded
	except Exception as e:
		log.info(f"Failed to parse message content as YAML ({e})")
	
	# Preset mode
	if message.startswith("#"):
		(preset, *prompt) = message[1:].split(" ")
		if preset not in imagen_presets:
			raise ValueError(f"Invalid preset \"{preset}\"")
		
		options = imagen_presets[preset]
		options["gen"]["prompt"] = " ".join(prompt)
		return options
	
	# Prompt mode
	return {
		"gen": {
			"prompt": message,
		},
	}

def time_sub(t1, t2):
	return datetime.combine(date.min, t1) - datetime.combine(date.min, t2)

def register_commands(polybot: PolyBot):
	bot = polybot.bot
	
	@bot.command(
		brief="Vous vous ennuiyez ? j'ai la solution !",
	)
	async def ennui(ctx: Context):
		message = random.choice([
			"Pti geoguesser ?\nhttps://www.geoguessr.com/",
			"Pti skribblio ?\nhttps://skribbl.io/",
			"Pti c??mantix ?\nhttps://cemantix.herokuapp.com/",
			"Pti p??dantix ?\nhttps://cemantix.herokuapp.com/pedantix",
			"Pti pixelmovie ?\nhttps://pixelmovie.github.io/",
			"Pti tusmo ?\nhttps://www.tusmo.xyz/",
			"Pti worldle ?\nhttps://worldle.teuteuf.fr/",
			"Pti framed ?\nhttps://framed.wtf/",
		])
		await polybot.send(message, reply_to=ctx.message)

	@bot.command(
		brief="Vous vous sentez mal ? regardez l'argent que vous gagnez pas seconde !",
	)
	async def salaire(ctx: Context):
		start_work = time(9, 0, 0)
		end_work = time(17, 0, 0)
		hourly_rate = 7

		# Horloge depuis minuit
		work_time = datetime.now().time()

		# Limit the work_time
		if work_time > end_work:
			work_time = end_work
		if work_time < start_work:
			work_time = start_work

		work_time = time_sub(work_time, start_work)
		
		gain = (work_time.seconds / 3600) * hourly_rate

		message = f"Vous avez gagn?? %.2f??? depuis le d??but de la journ??e\nhttps://tenor.com/view/wealth-gif-24406365" % gain
		await polybot.send(message, reply_to=ctx.message)

	@bot.command(
		brief="Vous avez faim ? regardez cette magnifique nourriture !",
	)
	async def morfal(ctx: Context):
		message = random.choice([
			"https://tenor.com/view/big-buger-eat-buger-the-rock-burger-gif-22532545",
			"https://tenor.com/view/burger-delicious-yummy-mouth-watering-gif-16353143",
			"https://tenor.com/view/mexican-cuisine-mexican-food-yummy-food-gif-17915340",
			"https://tenor.com/view/foodie-food-delicious-yummy-cravings-gif-17554117",
			"https://tenor.com/view/mukbang-food-mukbang-gifs-asmr-mukbang-korean-food-gif-22407553",
			"https://tenor.com/view/big-ed-thisisbiged-ed-big-fat-gif-21976378",
			"https://tenor.com/view/chinese-buffets-chinese-food-chinese-buffet-buffet-chinese-cuisine-gif-18397148",
			"https://tenor.com/view/sushiroll-shrimp-californiaroll-crunchyroll-nom-gif-4834623",
			"https://tenor.com/view/beef-meat-food-gif-15154168",
		])
		await polybot.send(message, reply_to=ctx.message)

	@bot.command(
		brief="Pong",
	)
	async def ping(ctx: Context):
		lat = bot.latency

		if math.isnan(lat):
			lat = 0

		message = f"{math.floor(lat * 1000)} ms"
		await polybot.send(message, reply_to=ctx.message)

	@bot.command(
		brief="Vous avez envie d'en finir ? attendez la fin de polytech !",
	)
	async def timetosuffer(ctx: Context):
		await polybot.send(gettimetosuffer(endofformation), reply_to=ctx.message)

	@bot.command(
		brief="Vous avez envie d'en finir ? attendez la fin de votre soufrance !",
	)
	async def timetosuffer_me(ctx: Context):
		await polybot.send(gettimetosuffer_ofuser(ctx.author.id), reply_to=ctx.message)

	@bot.command(
		brief="Vous avez envie d'en finir ? attendez la fin de la semaine !",
	)
	async def timetosuffer_we(ctx: Context):
		friday = datetime.now().date()
		day_delta = timedelta(days=1)

		# Set to this week's friday
		while friday.weekday() != 4:
			if friday.weekday() > 4:
				friday -= day_delta
			else:
				friday += day_delta

		endofweek = datetime.combine(friday, endofday)

		await polybot.send(gettimetosuffer(endofweek), reply_to=ctx.message)

	@bot.command(
		brief="Donne le status du bot",
	)
	async def info(ctx: Context):
		status = await polybot.status()
		message = f"Je suis polybot v{App.ver} {App.env} actif depuis {status['up_since']}\n"
		await polybot.send(message, reply_to=ctx.message)

	@bot.command(
		brief="Affiche le nombre de triggers actifs",
	)
	async def triggers(ctx: Context):
		message = f"Il y a {len(polybot.triggers)} triggers"
		await polybot.send(message, reply_to=ctx.message)

	@bot.command(
		brief="Met le bot en pause",
	)
	async def pause(ctx: Context):
		if ctx.author.id not in Users.admins:
			raise Exception("You don't have admin rights")
		await polybot.pause()

	@bot.command(
		brief="Reprend le bot",
	)
	async def unpause(ctx: Context):
		if ctx.author.id not in Users.admins:
			raise Exception("You don't have admin rights")
		await polybot.unpause()

	@bot.command(
		brief="Envie de musique ? ??coutez cette playlist !",
	)
	async def classics(ctx: Context):
		resp = random.choice([
			# Bangers
			"https://www.youtube.com/watch?v=s36eQwgPNSE",
			"https://www.youtube.com/watch?v=6JhVo2zS8hU",
			"https://www.youtube.com/watch?v=PGNiXGX2nLU",
			"https://www.youtube.com/watch?v=djV11Xbc914",
			"https://www.youtube.com/watch?v=urWV2OjAmUQ",
			"https://www.youtube.com/watch?v=HXdP15Ubu6M",
			"https://www.youtube.com/watch?v=4DuUejBkMqE",
			"https://www.youtube.com/watch?v=S5Xa31jYxYc",

			# Funny bangers
			"https://www.youtube.com/watch?v=2Nat0rOEMCA",
			"https://www.youtube.com/watch?v=M5a7mrwXVFs",
			"https://www.youtube.com/watch?v=-G3MLjqicC8",
			"https://www.youtube.com/watch?v=tYseHTv9Xx0",
			"https://www.youtube.com/watch?v=NBw2I3obQTY",
		])
		await polybot.send(resp, reply_to=ctx.message)

	@bot.command(
		brief="Une id??e r??volutionaire ? Transforme la en image !",
	)
	async def imagen(ctx: Context):
		content = ctx.message.content.replace(f"{App.command_prefix}imagen", "").strip()
		if content == "help" or content == "":
			await polybot.send(image_gen_help, reply_to=ctx.message)
			return

		image_gen_kwargs = get_imagen_options(content)

		# Check user has no job in queue
		for request in polybot.requests.values():
			if request["type"] == "imagen" and request["message"].author.id == ctx.message.author.id:
				raise Exception("You already have a job in queue")
		
		# Add job to queue
		polybot.requests[ctx.message.id]["type"] = "imagen"

		status_message = await polybot.send("Waiting for worker...", reply_to=ctx.message)
		image_gen_kwargs["status_message"] = None if status_message is None else status_message.id

		# Create job
		url = f"{App.api_url}/api/jobs/"
		async with aiohttp.ClientSession() as session:
			auth_header = await polybot.get_auth_header()
			resp = await session.post(url, json={
				"type": "imagen",
				"input_data": json.dumps(image_gen_kwargs),
			}, headers=auth_header)

			try:
				resp.raise_for_status()
			except Exception as e:
				raise Exception(f"Failed to create job ({resp.status} {resp.reason})")

			job = await resp.json()

			# Wait for job to finish
			# await polybot.edit(status_message, "Executing job...")
			log.info(f"Waiting for job {job['id']} to finish")
			t = time_now()
			while True:
				await asyncio.sleep(0.05)

				if time_now() - t > 300:
					raise Exception("Job timed out")
				
				resp = await session.get(f"{url}{job['id']}/", headers=auth_header)

				try:
					resp.raise_for_status()
				except Exception as e:
					raise Exception(f"Failed to get job ({resp.status} {resp.reason})")

				job = await resp.json()
				if job["output_data"] is not None:
					break

		# Job finished
		await polybot.delete(status_message)

		# Error or success
		result = json.loads(job["output_data"])
		if "error" in result:
			raise Exception(result["error"])
		result = result["result"]

		file_obj = BytesIO(base64.b64decode(result))

		await polybot.send(
			f"**{image_gen_kwargs['gen']['prompt']}** - (Generated in {time_now() - t:.2f} s)",
			file=discord.File(file_obj, "image.jpg"),
			reply_to=ctx.message
		)

	@bot.command(
		brief="Envie de GAME ?",
	)
	async def culture(ctx: Context):
		await do_quiz(polybot, ctx)
