#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/rebuild_framework.sh

function test_env_vars()
{
  rebuild_assert "[ '$TFOO_ENV1' = 'tfoo_env1' ]"
  rebuild_assert "[ '$TFOO_ENV2' = 'tfoo_env2' ]"
  rebuild_assert "[ '$TBAR_ENV1' = 'foo' ]"
  rebuild_assert "[ '$TBAR_ENV2' = 'bar' ]"
}

rebuild_testing_run_unit_tests
