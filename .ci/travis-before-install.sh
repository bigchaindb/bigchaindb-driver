#!/bin/bash

#if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
if [[ "${TOXENV}" == *-rdb ]]; then
    source /etc/lsb-release
    echo "deb http://download.rethinkdb.com/apt $DISTRIB_CODENAME main" | tee -a /etc/apt/sources.list.d/rethinkdb.list
    wget -qO- https://download.rethinkdb.com/apt/pubkey.gpg | apt-key add -
    apt-get update -qq
elif [[ "${TOXENV}" == *-mongodb ]]; then
    wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.4.4.tgz -O /tmp/mongodb.tgz
    tar -xvf /tmp/mongodb.tgz
    mkdir /tmp/mongodb-data
fi
