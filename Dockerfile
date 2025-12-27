FROM python:3.14-slim

WORKDIR /app

RUN apt update && apt install -y gcc

ENV PYTHONPATH=.

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "-m", "app"]

