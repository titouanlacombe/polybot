import random
random.seed()

from .Trigger import Trigger
from Config.Users import *

def prof_de_c(message):
	return random.choice([
		"Vous savez mon fils il joue au jeux vidéos",
		"Moi je fesait du pascal",
		"Vous connaissez le fortran ?",
		"Vous pouvez convertir des kilos en grammes ?",
		"Ca doit être Orange qui bug...",
		"Vous pouvez venir m'aider ?",
		"*Printers suffering in silence*",
		"*Appelle son fils*",
		"*Renvoie le même mail 3 fois*",
	])

def ping_pong(message):
	return random.choice([
		"https://tenor.com/view/vettel-in-wall-hit-the-wall-gif-11905373",
		"https://tenor.com/view/lets-go-the-rock-rock-go-rock-lets-go-lg-gif-18455293",
		"https://tenor.com/view/ping-pong-ping-pong-the-animation-peco-smile-gif-18194601",
	])

def alain(message):
	return random.choice([
		"https://tenor.com/view/funny-very-sloth-slow-gif-15401812",
		"https://tenor.com/view/sloth-crawling-slow-gif-9915689",
		"https://tenor.com/view/sweet-dreams-good-night-sloth-yawn-sleepy-gif-15429452",
		"https://tenor.com/view/sloth-slow-stamp-gif-8535595",
		"https://tenor.com/view/yes-zootopia-sloth-smile-happy-sloth-gif-14916132",
	])

def bonnecaze(message):
	return random.choice([
		"J'ai diagonalisé une matrice a 11 ans btw\nhttps://tenor.com/view/ross-friends-smug-smile-oops-gif-4195535",
		"Vous saviez que les masques sont une manipulation de masse ?",
		"Si macron passe je... je...",
		"Je connais bien car j'ai écrit un livre dessus\nhttps://tenor.com/view/ross-friends-smug-smile-oops-gif-4195535",
	])

def quafaf(message):
	return random.choice([
		"Bonchour les amis :)",
		"Alors les hypergraphes...",
		"Mais vous êtes un petit génie !",
		"La cuisine de ma femme est la meilleure",
		"Je vous ai ramené des croissants :)",
		"*prend le B1*\nhttps://tenor.com/view/creditos-creditosfinales-creditosmeme-the-end-gif-12638195",
		"https://tenor.com/view/clown-nose-joker-funny-dropped-gif-23619188",
		"Quafaf quand il pose des questions sur l'IA\nhttps://tenor.com/view/patrick-bateman-why-isnt-it-possible-you-stupid-bastard-christian-bale-gif-25703352"
	])

def leon(message):
	return random.choice([
		"pthread_create(send_to_rattrapages, NULL)",
		"MEMOIRE",
		"MUTEX",
		"SEMAPHORE",
		"Réviser le SE:\nhttps://tenor.com/view/oui-oue-eddy-malou-interview-gif-5034006",
		"Léon: *talk*\nUs:\nhttps://tenor.com/view/michael-scott-the-office-steve-carell-explain-like-im-five-eli5-gif-5356727",
	])

def durand(message):
	return random.choice([
		"https://tenor.com/view/gorilla-walking-run-gif-14877257",
		"https://tenor.com/view/funny-animals-walking-gorilla-ape-gif-11409190",
		"https://tenor.com/view/elaines-manager-beta-gang-gif-13851992",
	])

def jehanno(message):
	return random.choice([
		# "Entre les marocains et les polonais et les éxotiques pakistanais y'en a pas un pour rattraper l'autre...",
		None,
	])

triggers = [
	# Commandes de base
	Trigger(r'\bbonjour le bot\b', lambda m: "Salut :)", special_users=[titouan]),
	Trigger(r'\bbonjour le bot\b', lambda m: "https://tenor.com/view/monkey-look-the-other-way-look-away-awkward-weird-gif-17246188"),
	
	# profs
	# Trigger(r'\bquafaf', quafaf),
	Trigger(r'\bmavro', lambda m: "https://tenor.com/view/nileseyy-niles-peace-out-disappear-meme-disappearing-guy-checking-out-gif-25558985"),
	Trigger(r'\bbonnecaze\b', bonnecaze),
	Trigger(r'\bprof de c\b', prof_de_c),
	Trigger(r'\bleon\b', leon),
	# Trigger(r'\balain\b', alain),
	# Trigger(r'\bdurand\b', durand),
	Trigger(r'\boliveri\b', lambda m: "le GOAT"),
	Trigger(r'\bkristen\b', lambda m: "la GOAT"),
	# Trigger(r'\bjehanno\b', jehanno),
	Trigger(r'\bayache\b', lambda m: "https://tenor.com/view/nileseyy-niles-peace-out-disappear-meme-disappearing-guy-checking-out-gif-25558985"),
	Trigger(r'\btisserant\b', lambda m: "Tisserant...\nhttps://tenor.com/view/cat-catcry-gif-19131995"),
	Trigger(r'\bbanton\b', lambda m: "https://tenor.com/view/cat-catcry-gif-19131995"),
]
