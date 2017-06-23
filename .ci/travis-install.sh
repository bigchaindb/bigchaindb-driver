#!/bin/bash

set -e -x

pip install --upgrade pip
pip install --upgrade tox

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
    sudo apt-get install rethinkdb
    pip install bigchaindb==1.0.0rc1
    pip install --upgrade codecov
fi
