#!/bin/sh
# Hugging face cache fix
export TRANSFORMERS_CACHE="../data/hf_cache/transformers"

exec gunicorn -c gunicorn.conf.py Worker:app
