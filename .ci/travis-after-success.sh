#!/bin/bash

set -e -x

if [ "${TOXENV}" == "py36" ]; then
    codecov -v -f htmlcov/coverage.xml
fi
