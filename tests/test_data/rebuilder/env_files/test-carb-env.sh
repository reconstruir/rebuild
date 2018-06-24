#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_carb_env()
{
  bes_assert "[ '$LIBCARB_ENV1' = 'carb_env1' ]"
  bes_assert "[ '$LIBCARB_ENV2' = 'carb_env2' ]"
}

bes_testing_run_unit_tests
