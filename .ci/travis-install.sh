#!/bin/bash
# Copyright BigchainDB GmbH and BigchainDB contributors
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0


set -e -x

pip install --upgrade pip
pip install --upgrade tox

if [[ "${TOXENV}" == "py35" || "${TOXENV}" == "py36" ]]; then
    docker-compose build --no-cache bigchaindb bigchaindb-driver
    pip install --upgrade codecov
fi
