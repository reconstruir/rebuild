#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_env()
{
  output=$(libfoo.py one two tre)
  bes_assert "[ 'libfoo: one two tre' = '$output' ]"
}

bes_testing_run_unit_tests

