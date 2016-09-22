FROM python:3.5

RUN apt-get update && apt-get install -y vim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY . /usr/src/app/

RUN pip install --process-dependency-links "git+https://github.com/bigchaindb/bigchaindb.git@feat/586/integrate-tx-model"
RUN bigchaindb -y configure
