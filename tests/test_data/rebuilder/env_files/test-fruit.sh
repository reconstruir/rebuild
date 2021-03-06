#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_fruit_dot_py()
{
  output=$(fruit.py one two tre)
  bes_assert "[ 'water: a b c # carb: a b c # fiber: a b c # fruit: one two tre' = '$output' ]"
}

bes_testing_run_unit_tests
