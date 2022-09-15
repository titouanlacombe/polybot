#!/bin/sh
export POLYBOT_PORT=8080
export API_PORT=5000

exec supervisord -c ./Config/supervisord.conf
