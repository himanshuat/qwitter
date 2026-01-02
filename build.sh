#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input --settings=qwitter.settings.prod
python manage.py migrate --settings=qwitter.settings.prod