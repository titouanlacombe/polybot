import asyncio, discord, base64, logging, random
from discord.ext.commands import Context

from .PolyBot import PolyBot

api_url = "https://opentdb.com/api.php"
log = logging.getLogger(__name__)

async def get_question(polybot: PolyBot, **kwargs):
	kwargs.update({
		"amount": 1,
		"encode": "base64",
	})

	async with polybot.http_session.get(api_url, params=kwargs) as response:
		question = (await response.json())["results"][0]

	# Base64 decode
	for key in ["question", "correct_answer", "category", "type", "difficulty"]:
		question[key] = base64.b64decode(question[key]).decode()
	question["incorrect_answers"] = [base64.b64decode(a).decode() for a in question["incorrect_answers"]]

	formated_str = f"[{question['category']} - {question['difficulty']}] {question['question']}"
	formated_str += " (Time left {time_left}s)"

	options: list = question["incorrect_answers"] + [question["correct_answer"]]
	random.shuffle(options)
	for i, option in enumerate(options):
		formated_str += f"\n{i+1}. {option}"

	return formated_str, options.index(question["correct_answer"]) + 1

async def do_quiz(polybot: PolyBot, ctx: Context, **kwargs):
	log.info(f"Starting quiz with {kwargs}")

	question, correct_answer = await get_question(polybot, **kwargs)

	log.info(f"Question: {question}")

	winned = False
	responded = []

	# Subscribe to new messages to select winner
	@polybot.bot.listen()
	async def on_message(message: discord.Message):
		nonlocal winned, responded
		if not message.content.isdigit():
			return

		log.info(f"Got answer: \"{message.content}\" from {message.author.display_name}")
		if winned:
			log.info("Already winned, ignoring")
			return
		if message.author in responded:
			log.info("Already responded, ignoring")
			return
		responded.append(message.author)
		if int(message.content) != correct_answer:
			log.info("Wrong answer")
			return

		winned = True
		log.info("Winned")
		await polybot.send(f"Correct ! {message.author.mention} wins !", channel=ctx.channel)

	time_left = 10
	message = await polybot.send(question.format(time_left=time_left), channel=ctx.channel)

	while time_left > 0:
		await asyncio.sleep(1)
		time_left -= 1
		if message is not None:
			# Don't wait for message edit
			asyncio.create_task(polybot.edit(message, question.format(time_left=time_left)))

	# Unsubscribe
	polybot.bot.remove_listener(on_message)

	log.info("Expired")

	if not winned:
		log.info("Nobody winned")
		await polybot.send(f"No winner, the correct answer was {correct_answer}", channel=ctx.channel)
