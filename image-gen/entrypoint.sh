#!/bin/sh

exec gunicorn -c gunicorn.conf.py Flask:app
