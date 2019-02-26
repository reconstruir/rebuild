#!/bin/bash

set -e -x

ARGS="--stop --temp-dir ${REBUILD_TEMP_DIR} --verbose --no-env-deps --file-ignore-file .bes_test_internal_ignore --dont-hack-env"

_DEFAULT_UNIT_TESTS="*"
_DEFAULT_UNIT_TESTS="bin/test_rebuilder.py :test_one_project"

EGO_REBUILD_UNIT_TESTS=${EGO_REBUILD_UNIT_TESTS:-"${_DEFAULT_UNIT_TESTS}"}

_TESTS="${REBUILD_BUILD_DIR}/tests/${EGO_REBUILD_UNIT_TESTS}"

DEBUG=1 $(which bes_test.py) ${ARGS} ${_TESTS}
