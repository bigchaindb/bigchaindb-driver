FROM python:3.5

RUN apt-get update && apt-get install -y vim

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY . /usr/src/app/

# Until https://github.com/bigchaindb/bigchaindb/issues/559 is solved
RUN pip install "git+https://github.com/bigchaindb/bigchaindb.git"
RUN bigchaindb -y configure
