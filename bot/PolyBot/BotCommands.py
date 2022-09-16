import math, random
from datetime import datetime, date, time
from discord.ext.commands import Context

from .TimeToSuffer import gettimetosuffer, endofformation
import Config.App as App
import Config.Users as Users
from .PolyBot import PolyBot

random.seed()

def time_sub(t1, t2):
	return datetime.combine(date.min, t1) - datetime.combine(date.min, t2)

def register_commands(polybot: PolyBot):
	bot = polybot.bot
	
	@bot.command()
	async def ennui(ctx: Context):
		message = random.choice([
			"Pti geoguesser ?\nhttps://www.geoguessr.com/",
			"Pti skribblio ?\nhttps://skribbl.io/",
			"Pti cémantix ?\nhttps://cemantix.herokuapp.com/",
			"Pti pédantix ?\nhttps://cemantix.herokuapp.com/pedantix",
			"Pti pixelmovie ?\nhttps://pixelmovie.github.io/",
			"Pti tusmo ?\nhttps://www.tusmo.xyz/",
			# TODO include games from antoine daniel
			"Pti worldle ?\nhttps://worldle.teuteuf.fr/",
			"Pti framed ?\nhttps://framed.wtf/",
		])
		await polybot.send(message, ctx.channel)

	@bot.command()
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

		message = f"Vous avez gagné %.2f€ depuis le début de la journée\nhttps://tenor.com/view/wealth-gif-24406365" % gain
		await polybot.send(message, ctx.channel)

	@bot.command()
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
		await polybot.send(message, ctx.channel)

	@bot.command()
	async def ping(ctx: Context):
		lat = bot.latency

		if math.isnan(lat):
			lat = 0

		message = f"Ta gueule ({math.floor(lat * 1000)} ms)"
		await polybot.send(message, ctx.channel)

	@bot.command()
	async def timetosuffer(ctx: Context):
		message = gettimetosuffer(endofformation)
		await polybot.send(message, ctx.channel)

	@bot.command()
	async def info(ctx: Context):
		status = await polybot.status()
		message = f"Je suis PolyBot v{App.ver} {App.env} actif depuis {status['up_since']}\n"
		await polybot.send(message, ctx.channel)

	@bot.command()
	async def triggers(ctx: Context):
		# _triggers = len(rpc_handler.triggers)
		_triggers = "TODO"
		message = f"Il y a {_triggers} triggers"
		await polybot.send(message, ctx.channel)

	@bot.command()
	async def pause(ctx: Context):
		if ctx.author.display_name not in Users.admins:
			raise Exception("You don't have admin rights")

		# rpc_handler.pause()
		await polybot.send("Ok")

	@bot.command()
	async def classics(ctx: Context):
		resp = random.choice([
			"https://www.youtube.com/watch?v=s36eQwgPNSE",
			"https://www.youtube.com/watch?v=6JhVo2zS8hU",
		])
		await polybot.send(resp, ctx.channel)
