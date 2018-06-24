#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_water_env()
{
  bes_assert "[ $LIBWATER_ENV1 = water_env1 ]"
  bes_assert "[ $LIBWATER_ENV2 = water_env2 ]"
}

bes_testing_run_unit_tests
