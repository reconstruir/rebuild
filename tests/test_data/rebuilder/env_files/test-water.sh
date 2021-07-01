#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.bash

function test_water_dot_py()
{
  output=$(water.py one two tre)
  bes_assert "[ 'water: one two tre' = '$output' ]"
}

bes_testing_run_unit_tests
