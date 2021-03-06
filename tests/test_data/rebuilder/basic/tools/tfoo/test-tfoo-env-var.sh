#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_env()
{
  bes_assert "[ $TFOO_ENV1 = tfoo_env1 ]"
  bes_assert "[ $TFOO_ENV2 = tfoo_env2 ]"
}

bes_testing_run_unit_tests
