#!/bin/sh

if [ "$CRON" != "cron" ] && [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
	python manage.py collectstatic --no-input --clear
	python manage.py makemigrations api
	python manage.py migrate --noinput
  python manage.py loaddata data.json
	python manage.py createsuperuser --username=ns --email=merzlyakov02@gmail.com --noinput
fi

if [ "$CRON" = "cron" ] && [ "$DATABASE" = "postgres" ] 
then
  echo "Waiting for postgres... from cron!"

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started (CRON)"
  echo "hello from cron!"
  python manage.py crontab add
fi


exec "$@"