import config.Filesystem as Filesystem
from copy import deepcopy

def get_dict_conf(
	file_path,
	level='INFO',
	maxBytes=1024 * 1024 * 10,
	backupCount=5,
	format='[{asctime}] {levelname}:{name}: {message}',
	datefmt='%Y-%m-%d %H:%M:%S',
):
	return {
		'version': 1,

		'formatters': {
			'standard': {
				'format': format,
				'datefmt': datefmt,
				'style': '{'
			},
		},
		'handlers': {
			'console': {
				'level': level,
				'formatter': 'standard',
				'class': 'logging.handlers.RotatingFileHandler',
				'maxBytes': maxBytes,
				'backupCount': backupCount,
				'filename': str(Filesystem.logs_dir / f"{file_path}.log"),
			},
		},
		'loggers': {
			'': {
				'handlers': ['console'],
				'level': level,
				'propagate': False
			},
		}, 
	}

def get_gunicorn_dict_conf(filename, **kwargs):
	conf = deepcopy(get_dict_conf(filename, **kwargs))
	conf['disable_existing_loggers'] = True
	conf['loggers']['gunicorn'] = conf['loggers'].pop('')
	return conf
