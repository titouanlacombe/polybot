#!/bin/sh
# Hugging face cache fix
export TRANSFORMERS_CACHE="../data/hf_cache/transformers"

# Pytorch patch
export HSA_OVERRIDE_GFX_VERSION=10.3.0

exec gunicorn -c gunicorn.conf.py Worker:app
