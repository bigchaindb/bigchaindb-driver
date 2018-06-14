#!/bin/bash

set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  ci_env=`bash <(curl -s https://codecov.io/env)`
  docker-compose run --rm bigchaindb-driver pytest -v -e ci_env=`bash <(curl -s https://codecov.io/env)`
else
  tox -e ${TOXENV}
fi
