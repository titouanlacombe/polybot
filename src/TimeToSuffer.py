from datetime import datetime, timedelta, time, date
import random
import config.Users as Users

# 14h UTC is 16h in Paris
endofday = time(14, 30, 0)
endofformation = datetime.combine(date(2023, 9, 30), endofday)

def gettimetosuffer(endofsuffering):
	# Le 30 Juin 2023 a 16h30
	timetosuffer: timedelta = endofsuffering - datetime.now()

	# If suffering is finished, display celebration message
	if timetosuffer.days < 0:
		return "Souffrance terminée !\n" \
			+ random.choice([
			"https://tenor.com/view/baby-yoda-babyyoda-gif-20491479",
			"https://tenor.com/view/kermit-frog-panic-frantic-yay-gif-16814992",
			"https://tenor.com/view/happy-dancing-celebrate-excited-gif-22624142",
			"https://tenor.com/view/leonardo-dicaprio-cheers-%C5%9Ferefe-celebration-celebrating-gif-20368613",
			"https://tenor.com/view/celebration-celebrate-yay-gif-24947639",
			"https://tenor.com/view/dance-party-happy-fun-weekend-gif-22833066",
			"https://tenor.com/view/celebrate-happy-you-did-it-oprah-winfrey-gif-16871108",
			"https://tenor.com/view/woo-dance-dancing-celebrate-gif-18613546",
			"https://tenor.com/view/shaq-wiggle-shimmy-shake-excited-gif-12957471",
		])

	# Else, display remaining time
	hours = timetosuffer.seconds // 3600
	minutes = (timetosuffer.seconds // 60) % 60
	seconds = timetosuffer.seconds % 60
	
	return f"Il reste {timetosuffer.days} jours {hours} heures {minutes} minutes et {seconds} secondes a souffrir...\n" \
		+ random.choice([
			"https://tenor.com/view/cat-driving-serious-cat-driving-hold-on-gif-16076083",
			"https://tenor.com/view/wearytraveler-delayedflight-dead-tired-sleepy-gif-22624372",
			"https://tenor.com/view/cookie-stay-strong-strong-covid-covid19-gif-21844017",
			"https://tenor.com/view/big-bang-theroy-stressed-hyperventilating-gif-24158173",
	])

users_endofsuffering = {
	# Users.titouan: datetime.combine(date(2023, 6, 30), endofday),
	# Users.guillaume: datetime.combine(date(2023, 6, 30), endofday),
	# Users.quentin: datetime.combine(date(2023, 6, 30), endofday),
	# Users.karim: datetime.combine(date(2023, 6, 30), endofday),
	# Users.ghassan: datetime.combine(date(2023, 6, 30), endofday),
	# Users.nathan: datetime.combine(date(2023, 6, 30), endofday),
	# Users.polybot: datetime.combine(date(2023, 6, 30), endofday),
	Users.dev_user: datetime.combine(date(2023, 6, 30), endofday),
}

def gettimetosuffer_ofuser(user):
	if user in users_endofsuffering:
		return gettimetosuffer(users_endofsuffering[user])
	else:
		return "Vous n'avez pas de date de fin de souffrance."
	