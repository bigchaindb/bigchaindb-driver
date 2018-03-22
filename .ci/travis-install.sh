#!/bin/bash

set -e -x

pip install --upgrade pip
pip install --upgrade tox

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
    docker-compose build --no-cache bigchaindb bigchaindb-driver
    pip install --upgrade codecov
fi
