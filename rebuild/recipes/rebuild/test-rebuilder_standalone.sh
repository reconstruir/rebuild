#!/bin/bash

set -e

source ${REBUILD_SHELL_FRAMEWORK_DIR}/bes_shell.bash

set -x

function test_rebuilder_version()
{
  local _exe=$(which rebuilder)
  local _version=$(${_exe} --version | head -1 | awk '{ print $1; }')
  bes_assert "[ ${_version} = ${REBUILD_PACKAGE_FULL_VERSION} ]"
}

function test_rebuilder_test_project()
{
  local _exe=$(which rebuilder)
  unset PYTHONPATH
  cp -a ${REBUILD_RECIPE_DIR}/test_project/* .
  ${_exe} --verbose --storage-config storage.config --sources-config-name local_sources -f test.reproject
}

bes_testing_run_unit_tests
