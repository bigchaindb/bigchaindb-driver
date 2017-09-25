#!/bin/bash

set -e -x

pip install --upgrade pip

if [[ -n ${TOXENV} ]]; then
    pip install --upgrade tox
fi

if [[ "${TOXENV}" == py3*-* ]]; then
    pip install --upgrade codecov
fi
