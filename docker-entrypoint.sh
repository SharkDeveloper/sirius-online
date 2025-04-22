#!/bin/sh

set -e

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Collect static
#python manage.py collectstatic --noinput

# Execute the CMD
exec "$@"
