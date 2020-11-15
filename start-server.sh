#!/usr/bin/env bash

# start-server.sh

(cd goldiba-back; python manage.py migrate)

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (cd goldiba-back; python manage.py createsuperuser --no-input)
fi
(cd goldiba-back; gunicorn api.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"

