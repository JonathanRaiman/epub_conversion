#!/bin/bash

# stop script on error and print it
set -e
# inform me of undefined variables
set -u
# handle cascading failures well
set -o pipefail

SCRIPT_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

rm ${SCRIPT_DIR}/dist/*
python3 setup.py clean
python3 setup.py sdist
twine upload ${SCRIPT_DIR}/dist/* --verbose
