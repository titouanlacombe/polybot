import datetime
import discord

# Sender implement methods send and edit
class DiscordProgressBar:
	def __init__(self, sender, total: int, title=None):
		self.sender = sender
		self.title = title
		self.total = total

		self.current = 0
		self.message: discord.Message = None
		self.start_time = None

	async def start(self):
		self.start_time = datetime.datetime.now()
		self.message = await self.sender.send(self.render())

	async def update(self, current: int):
		self.current = current
		if self.message is not None:
			await self.sender.edit(self.message, self.render())

	async def increment(self):
		self.current += 1
		await self.update(self.current)

	async def finish(self):
		if self.message is not None:
			await self.message.delete()
	
	def render(self):
		percent = self.current / self.total
		bar = "#" * int(percent * 20)
		bar = bar.ljust(20, "-")
		eta = self.eta()
		return f"** {self.title} **\n{self.current}/{self.total} | [{bar}] {percent * 100:.2f}% | Elapsed: {int(self.elapsed())} s | ETA: {int(eta) if eta else '∞'} s"

	def eta(self):
		if self.current == 0:
			return None
		return (self.total - self.current) * self.elapsed() / self.current

	def elapsed(self):
		time_delta: datetime.timedelta = datetime.datetime.now() - self.start_time
		return time_delta.total_seconds()
