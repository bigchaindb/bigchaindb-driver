#!/bin/bash

set -e -x

if [[ "${TOXENV}" == *-rdb ]]; then
    rethinkdb --daemon
    export BIGCHAINDB_KEYPAIR_PUBLIC=GW1nrdZm4mbVC8ePeiGWz6DqHexqewqy5teURVHi3RG4
    export BIGCHAINDB_KEYPAIR_PRIVATE=2kQgBtQnHoauw8QchKM7xYvEBW1QDoHzhBsCL9Vi1AzB 

    # Start BigchainDB in the background and ignore any output
    bigchaindb start >/dev/null 2>&1 &
elif [[ "${BIGCHAINDB_DATABASE_BACKEND}" == mongodb ]]; then
    # Connect to MongoDB on port 27017 via a normal, unsecure connection if
    # BIGCHAINDB_DATABASE_SSL is unset.
    # It is unset in this case in .travis.yml.
    wget https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1404-3.4.4.tgz -O /tmp/mongodb.tgz
    tar -xvf /tmp/mongodb.tgz
    mkdir /tmp/mongodb-data
    ${PWD}/mongodb-linux-x86_64-ubuntu1404-3.4.4/bin/mongod \
        --dbpath=/tmp/mongodb-data --replSet=bigchain-rs &> /dev/null &
fi
