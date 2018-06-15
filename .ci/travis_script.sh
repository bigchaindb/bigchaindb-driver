#!/bin/bash

set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  docker-compose run --rm bigchaindb-driver pytest -v --cov=bigchaindb_driver --cov-report html
  bash <(curl -s https://codecov.io/bash)
else
  tox -e ${TOXENV}
fi
