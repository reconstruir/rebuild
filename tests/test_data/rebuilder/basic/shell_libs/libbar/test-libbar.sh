#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_framework.sh
source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/bes_testing.sh

function test_libbar_dot_py()
{
  bes_assert "[ 'libfoo: a b c # libbar: one two tre' = '$(libbar.py one two tre)' ]"
}

bes_testing_run_unit_tests
