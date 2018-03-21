#!/bin/bash

set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  docker-compose up --abort-on-container-exit bigchaindb-driver
else
  tox -e ${TOXENV}
fi
