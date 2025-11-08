#!/bin/sh

set -e

cd /app || exit 1

python /entrypoint.py

exec "$@"
