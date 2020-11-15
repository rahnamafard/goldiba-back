#!/usr/bin/env bash

set -euo pipefail

python manage.py migrate
chmod +rwx db.sqlite3
python manage.py runserver
