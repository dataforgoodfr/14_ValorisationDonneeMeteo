#!/bin/sh
set -e

echo "Applying database migrations..."
uv run python manage.py migrate --noinput


echo "Collecting static files..."
uv run python manage.py collectstatic --noinput

<<<<<<< HEAD
exec "$@"
=======
exec "$@"
>>>>>>> 9348c3e (feat: setup build and push to GHCR)
