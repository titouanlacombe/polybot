import config.Filesystem as Filesystem

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
		'disable_existing_loggers': True,

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
			'gunicorn': {
				'handlers': ['console'],
				'level': level,
				'propagate': False
			},
		}, 
	}
