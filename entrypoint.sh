#!/bin/sh

set -e

cd /app || exit 1

# COMENTE OU EXCLUA ESTA LINHA:
# python /entrypoint.py 

# O Gunicorn/Django só será executado DEPOIS que o healthcheck
# do 'db' já tiver passado, graças ao docker-compose.
exec "$@"