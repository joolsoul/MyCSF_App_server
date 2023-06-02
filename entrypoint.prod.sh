#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
	python manage.py collectstatic --no-input --clear
	python manage.py makemigrations api
	python manage.py migrate --noinput
	python manage.py createsuperuser --username=ns --email=merzlyakov02@gmail.com --noinput
fi



exec "$@"