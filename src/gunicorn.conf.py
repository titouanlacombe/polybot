import Config.App as App
import Config.Logging as Logging

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

logconfig_dict = Logging.get_dict_conf('api')
