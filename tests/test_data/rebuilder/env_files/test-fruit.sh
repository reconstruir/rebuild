#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/rebuild_framework.sh

function test_fruit_dot_py()
{
  output=$(fruit.py one two tre)
  rebuild_assert "[ 'water: a b c # carb: a b c # fiber: a b c # fruit: one two tre' = '$output' ]"
}

rebuild_testing_run_unit_tests
