FROM python:3.10.4-slim-buster

# Create user
RUN useradd app -ms /bin/bash
WORKDIR /home/app

# Install linux packages
RUN apt update && apt install -y --no-install-recommends \
	bash \
	curl \
	# Gunicorn reload
	inotify-tools \
	# Clear apt cache
	&& apt clean \
	&& rm -rf /var/lib/apt/lists/*

# Python requirements
COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install --no-cache-dir -r ./requirements.txt

# Sources
COPY ./src ./src
RUN chown app:app -R /home/app
WORKDIR /home/app/src

# Entrypoint
USER app
CMD ["./entrypoint.sh"]
