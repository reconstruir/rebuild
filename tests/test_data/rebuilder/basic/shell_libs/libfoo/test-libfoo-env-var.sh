#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_env()
{
  bes_assert "[ $LIBFOO_ENV1 = libfoo_env1 ]"
  bes_assert "[ $LIBFOO_ENV2 = libfoo_env2 ]"
}

bes_testing_run_unit_tests
