import datetime

# Sender implement methods send, edit and delete
class DiscordProgressBar:
	def __init__(self, sender, total: int, title=None):
		self.sender = sender
		self.total = total
		self.title = title

		self.current = 0
		self.message = None
		self.start_time = None

		# Bar style
		self.bar_length = 10
		self.full_char = "#"
		self.empty_char = "-"
		self.format = "** {title} **\n{current}/{total} | [{bar}] {percent}% | Elapsed: {elapsed}s | ETA: {eta}s"

	async def start(self):
		self.start_time = datetime.datetime.now()
		self.message = await self.sender.send(self.render())

	async def update(self, current: int):
		self.current = current
		if self.message is not None:
			await self.sender.edit(self.message, self.render())

	async def increment(self):
		await self.update(self.current + 1)

	async def finish(self):
		if self.message is not None:
			await self.sender.delete(self.message)
	
	def render(self):
		percent = self.current / self.total
		bar = self.full_char * int(percent * self.bar_length)
		bar = bar.ljust(self.bar_length, self.empty_char)
		eta = self.eta()
		eta = int(eta) if eta is not None else "N/A"
		return self.format.format(
			title=self.title,
			current=self.current,
			total=self.total,
			bar=bar,
			percent=int(percent * 100),
			elapsed=int(self.elapsed()),
			eta=eta
		)

	def eta(self):
		if self.current == 0:
			return None
		return (self.total - self.current) * self.elapsed() / self.current

	def elapsed(self):
		time_delta: datetime.timedelta = datetime.datetime.now() - self.start_time
		return time_delta.total_seconds()
