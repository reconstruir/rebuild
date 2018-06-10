#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_env_vars()
{
  bes_assert "[ '$LIBFOO_ENV1' = 'libfoo_env1' ]"
  bes_assert "[ '$LIBFOO_ENV2' = 'libfoo_env2' ]"
  bes_assert "[ '$LIBBAR_ENV1' = 'libbar_env1' ]"
  bes_assert "[ '$LIBBAR_ENV2' = 'libbar_env2' ]"
}

bes_testing_run_unit_tests
