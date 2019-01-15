#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh

function test_env()
{
  rebuild_assert "[ $TFOO_ENV1 = tfoo_env1 ]"
  rebuild_assert "[ $TFOO_ENV2 = tfoo_env2 ]"
}

bes_testing_run_unit_tests
