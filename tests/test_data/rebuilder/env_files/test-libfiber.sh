#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_libfiber_dot_py()
{
  bes_assert "[ 'libwater: a b c # libfiber: one two tre' = '$(libfiber.py one two tre)' ]"
}

bes_testing_run_unit_tests
