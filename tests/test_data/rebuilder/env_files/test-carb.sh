#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh

function test_carb_dot_py()
{
  output=$(carb.py one two tre)
  rebuild_assert "[ 'carb: one two tre' = '$output' ]"
}

bes_testing_run_unit_tests
