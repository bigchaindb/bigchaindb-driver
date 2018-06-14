#!/bin/bash

set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  docker-compose run --rm bigchaindb-driver pytest -v -e
  bash <(curl -s https://codecov.io/env)
else
  tox -e ${TOXENV}
fi
