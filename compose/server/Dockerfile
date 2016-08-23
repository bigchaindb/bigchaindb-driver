FROM python:3.5

RUN apt-get update && apt-get install vim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY . /usr/src/app/

RUN pip install "git+https://github.com/bigchaindb/bigchaindb.git"
