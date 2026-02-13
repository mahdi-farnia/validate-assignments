FROM python:3.14-alpine

WORKDIR /app

RUN apk update && apk add --no-cache build-base

RUN adduser -DH validator && \
    addgroup apps && \
    addgroup validator apps

ENV PYTHONPATH=.

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

USER validator

ENTRYPOINT ["python", "-m", "app"]

