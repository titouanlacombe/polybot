#!/bin/sh
# Hugging face cache fix
export TRANSFORMERS_CACHE="../data/hf_cache/transformers"

echo "Initializing cache..."
# TODO Fix not exit on error
python3 -m setup_pipeline

echo "Launching app..."
exec gunicorn -c gunicorn.conf.py Flask:app
