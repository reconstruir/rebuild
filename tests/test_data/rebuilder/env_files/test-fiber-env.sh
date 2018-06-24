#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_fiber_env()
{
  bes_assert "[ '$LIBFIBER_ENV1' = 'fiber_env1' ]"
  bes_assert "[ '$LIBFIBER_ENV2' = 'fiber_env2' ]"
}

bes_testing_run_unit_tests
