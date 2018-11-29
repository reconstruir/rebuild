#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/rebuild_framework.sh

function test_water_dot_py()
{
  output=$(water.py one two tre)
  rebuild_assert "[ 'water: one two tre' = '$output' ]"
}

rebuild_testing_run_unit_tests
