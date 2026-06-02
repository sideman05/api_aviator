#!/usr/bin/env bash
set -euo pipefail

python manage.py migrate --noinput
# Use threaded workers so streaming endpoints (which call time.sleep) don't block the whole worker.
# Reduce worker count to lower memory usage on small Render instances and increase timeout.
GUNICORN_WORKERS=${GUNICORN_WORKERS:-1}
GUNICORN_THREADS=${GUNICORN_THREADS:-4}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
exec gunicorn aviator_backend.wsgi:application \
	--workers "$GUNICORN_WORKERS" \
	--worker-class gthread \
	--threads "$GUNICORN_THREADS" \
	--timeout "$GUNICORN_TIMEOUT" \
	--log-level info
