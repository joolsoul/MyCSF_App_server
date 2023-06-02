###########
# BUILDER #
###########

FROM python:3.9.16-alpine as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
	&& apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev libffi-dev

RUN pip install --upgrade pip
# RUN pip install flake8==3.9.2
COPY . .
RUN rm -rf venv
# RUN flake8 --ignore=E501,F401 .

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

#########
# FINAL #
#########

FROM python:3.9.16-alpine

RUN mkdir -p /home/app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN apk update && apk add libpq jpeg-dev zlib-dev libjpeg
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.prod.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.prod.sh
RUN chmod +x  $APP_HOME/entrypoint.prod.sh

COPY . $APP_HOME

ENTRYPOINT ["/home/app/web/entrypoint.prod.sh"]