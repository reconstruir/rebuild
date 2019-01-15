#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh

function test_env_vars()
{
  rebuild_assert "[ '$CODEGEN_ENV1' = 'x_' ]"
  rebuild_assert "[ '$CODEGEN_ENV2' = 'y_' ]"
}

bes_testing_run_unit_tests
