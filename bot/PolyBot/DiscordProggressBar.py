import datetime
import discord

class DiscordProgressBar:
	def __init__(self, send_callback, total: int, title=None):
		self.send_f = send_callback
		self.title = title
		self.total = total

		self.current = 0
		self.message: discord.Message = None
		self.start_time = None

	async def start(self):
		self.start_time = datetime.datetime.now()
		self.message = await self.send_f(self.render())

	async def update(self, current: int):
		self.current = current
		await self.message.edit(content=self.render())

	async def increment(self):
		self.current += 1
		await self.update(self.current)

	async def finish(self):
		await self.message.delete()
	
	def render(self):
		percent = self.current / self.total
		bar = "#" * int(percent * 20)
		bar = bar.ljust(20, "-")
		return f"** {self.title} **\n{self.current}/{self.total} | [{bar}] {percent * 100:.2f}% | Elapsed: {int(self.elapsed())} s | ETA: {self.eta()} s"

	def eta(self):
		if self.current == 0:
			return "∞"
		return (self.total - self.current) * self.elapsed() / self.current

	def elapsed(self):
		time_delta: datetime.timedelta = datetime.datetime.now() - self.start_time
		return time_delta.total_seconds()
