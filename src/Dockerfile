FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
           openssl-dev libffi-dev gcc musl-dev python3-dev \
           postgresql-dev bash curl \
    && pip install --upgrade pip setuptools wheel build \
    && pip install -r requirements.txt


COPY . /usr/src/app