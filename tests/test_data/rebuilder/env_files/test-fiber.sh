#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.bash

function test_fiber_dot_py()
{
  output=$(fiber.py one two tre)
  bes_assert "[ 'carb: a b c # fiber: one two tre' = '$output' ]"
}

bes_testing_run_unit_tests
