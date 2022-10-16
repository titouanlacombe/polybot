import os

bind = f"0.0.0.0:{os.getenv('IMAGE_GEN_PORT', 8000)}"
reload = True

# Keep those workers because stable diffusion use all of the RAM
workers = 1
threads = 10

# max_requests = 3
# max_requests_jitter = 2
capture_output = True
timeout = 60 * 10 # minutes

loglevel = "info"
accesslog = "../data/logs/image-gen.log"
errorlog = "../data/logs/image-gen.log"
access_log_format = "%(r)s responded %(s)s in %(M)s ms"
