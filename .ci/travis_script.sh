#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
  docker-compose run --rm bigchaindb-driver pytest -v --cov=bigchaindb_driver --cov-report xml:htmlcov/coverage.xml
else
  tox -e ${TOXENV}
fi
