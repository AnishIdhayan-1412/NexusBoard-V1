#!/bin/sh
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Starting server..."
exec gunicorn nexusboard.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-2} \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
