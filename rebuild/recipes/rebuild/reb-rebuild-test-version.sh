#!/bin/bash

set -e -x

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.bash

function test_version()
{
  local _rebuilder_py=$(which rebuilder.py)
  local _rebuild_version=$(${_rebuilder_py} --version | awk '{ print $1; }')
  bes_assert "[ ${_rebuild_version} = ${REBUILD_PACKAGE_FULL_VERSION} ]"
}

bes_testing_run_unit_tests
