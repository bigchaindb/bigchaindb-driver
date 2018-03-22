#!/bin/bash

set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  docker-compose run --rm bigchaindb-driver pytest -v
else
  tox -e ${TOXENV}
fi
