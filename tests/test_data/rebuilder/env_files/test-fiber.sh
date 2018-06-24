#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_fiber_dot_py()
{
  output=$(fiber.py one two tre)
  bes_assert "[ 'fiber: one two tre' = '$output' ]"
}

bes_testing_run_unit_tests
