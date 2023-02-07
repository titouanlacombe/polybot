from Config.Filesystem import logs_dir
import Config.App as App

bind=f"{App.api_host}:{App.api_port}"
wsgi_app="flask_app:app"
threads=10

if App.in_pro or App.in_pre:
	workers=2
	preload_app=True
else:
	workers=1
	reload=True

max_requests=100
max_requests_jitter=10
capture_output=True

access_log_format = "%(r)s responded %(s)s in %(M)s ms"

logconfig_dict = {
	'version': 1,
	'disable_existing_loggers': True,

	'formatters': {
		'standard': {
			'format': "[{asctime}] {levelname}:{name}: {message}",
			'datefmt': "%Y-%m-%d %H:%M:%S",
			'style': '{'
		},
	},
	'handlers': {
		'console': {
			'level': 'INFO',
			'formatter': 'standard',
			'class': 'logging.handlers.RotatingFileHandler',
			'maxBytes': 1024 * 1024 * 10,  # 10 MB
			'backupCount': 5,
			'filename': str(logs_dir / 'api.log'),
		},
	},
	'loggers': {
		'gunicorn': {
			'handlers': ['console'],
			'level': 'INFO',
			'propagate': False
		},
	}, 
}
