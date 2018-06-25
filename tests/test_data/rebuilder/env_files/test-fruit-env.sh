#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_fruit_env()
{
  bes_assert "[ '$LIBCARB_ENV1' = 'carb_env1' ]"
  bes_assert "[ '$LIBCARB_ENV2' = 'carb_env2' ]"
  bes_assert "[ '$LIBFIBER_ENV1' = 'fiber_env1' ]"
  bes_assert "[ '$LIBFIBER_ENV2' = 'fiber_env2' ]"
  bes_assert "[ '$LIBFRUIT_ENV1' = 'fruit_env1' ]"
  bes_assert "[ '$LIBFRUIT_ENV2' = 'fruit_env2' ]"
  bes_assert "[ '$LIBWATER_ENV1' = 'water_env1' ]"
  bes_assert "[ '$LIBWATER_ENV2' = 'water_env2' ]"
}

bes_testing_run_unit_tests
