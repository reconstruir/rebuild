#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh

function test_tbar_dot_py()
{
  bes_assert "[ 'tfoo: a b c # tbar: one two tre' = '$(tbar.py one two tre)' ]"
}

bes_testing_run_unit_tests
