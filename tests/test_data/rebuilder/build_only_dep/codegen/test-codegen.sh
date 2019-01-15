#!/bin/bash

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.sh

function test_codegen_dot_py()
{
    actual=$(codegen.py a b c | tr -s '\n' ' ')
    bes_assert "[ ' #include \"a.h\" int x_y_a_b() { return c; } ' = '${actual}' ]"
}

bes_testing_run_unit_tests
