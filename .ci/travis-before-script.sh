#!/bin/bash

set -e -x

if [[ "${TOXENV}" == "py36" ]]; then
    docker-compose up -d bigchaindb
fi
