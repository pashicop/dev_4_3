FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y \
    iputils-ping\
    && rm -rf /var/lib/apt/lists/*

COPY . .

ENV TZ=Europe/Moscow

CMD [ "python3", "-u", "main.py"]