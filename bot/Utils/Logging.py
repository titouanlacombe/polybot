import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from Config.App import env

def getFormat(_env=None):
	if _env is None:
		_env = env[:3].upper()
	return "[{asctime}] " + _env + "-{levelname}:{name}: {message}", '%Y-%m-%d %H:%M:%S'

def basicConfig(logs_dir: Path, name="app", level=logging.INFO, env=None):
	logs_dir.mkdir(parents=True, exist_ok=True)

	# Build formatter
	fmt, datefmt = getFormat()
	formatter = logging.Formatter(
		fmt=fmt,
		datefmt=datefmt,
		style='{'
	)

	# Build file handler
	fh = RotatingFileHandler(logs_dir / f"{name}.log", maxBytes=10 * 1024 * 1024, backupCount=10)
	fh.setLevel(level)
	fh.setFormatter(formatter)

	root = logging.getLogger()
	root.setLevel(level)
	root.addHandler(fh)

	return fh, formatter, root
	