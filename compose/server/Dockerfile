FROM python:3.6.2rc1

RUN apt-get update && apt-get install -y vim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip ipdb ipython

COPY . /usr/src/app/

RUN pip install bigchaindb==1.0.0rc1
