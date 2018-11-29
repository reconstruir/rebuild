#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/env/rebuild_framework.sh

function test_tbar_dot_py()
{
  rebuild_assert "[ 'tfoo: a b c # tbar: one two tre' = '$(tbar.py one two tre)' ]"
}

rebuild_testing_run_unit_tests
