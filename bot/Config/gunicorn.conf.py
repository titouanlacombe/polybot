import os
from Utils.Logging import getFormat
from Config.Filesystem import logs_dir
import Config.App as App

bind=f"0.0.0.0:{os.environ['POLYBOT_API_PORT']}"

if App.in_pro() or App.in_pre():
	workers=2
	threads=10
	preload_app=True
else:
	workers=1
	threads=1
	reload=True

max_requests=100
max_requests_jitter=10
capture_output=True

access_log_format = "%(r)s responded %(s)s in %(M)s ms"

fmt, datefmt = getFormat()
logconfig_dict = {
	'version': 1,
	'disable_existing_loggers': True,

	'formatters': {
		'standard': {
			'format': fmt,
			'datefmt': datefmt,
			'style': '{'
		},
	},
	'handlers': {
		'console': {
			'level': 'INFO',
			'formatter': 'standard',
			'class': 'logging.FileHandler',
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
