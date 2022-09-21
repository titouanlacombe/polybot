bind = "0.0.0.0:80"

workers = 1
threads = 1
reload = True

# max_requests = 3
# max_requests_jitter = 2
capture_output = True
timeout = 60 * 5 # 5 minutes

loglevel = "info"
accesslog = "../data/logs/image-gen.log"
errorlog = "../data/logs/image-gen.log"
access_log_format = "%(r)s responded %(s)s in %(M)s ms"
