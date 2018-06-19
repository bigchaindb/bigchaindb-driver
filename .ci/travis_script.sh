#!/bin/bash

set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  docker-compose run --rm bigchaindb-driver pytest -v --cov=bigchaindb_driver --cov-report xml:htmlcov/coverage.xml
else
  tox -e ${TOXENV}
fi
