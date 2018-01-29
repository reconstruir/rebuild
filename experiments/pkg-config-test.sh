#!/bin/bash

NAME=$(basename $0)

function assert()
{
  eval "${@}"
  local _rv=$?
  if [ $_rv -ne 0 ]; then
    echo "FAILED: ${@}"
    exit 1  
  fi
}

function test_list_all()
{
  local _exe=$1
  local _log=$2
  assert test -n "$_exe"
  assert test -n "$_log"
  $_exe --list-all | sort >& $_log
}

function test_print_requires()
{
  local _exe=$1
  local _log=$2
  assert test -n "$_exe"
  assert test -n "$_log"
  $_exe --print-requires $($_exe --list-all | awk '{ print $1; }' | sort) >& $_log
}

function main()
{
  if [ $# -ne 2 ]; then
    echo "Usage: $NAME: exe1 exe2."
    return 1
  fi

  local _exe1=$1
  local _exe2=$2
  local _exe1_name=$(basename $_exe1)
  local _exe2_name=$(basename $_exe2)
  local _log_dir=$TMPDIR/pkg-config-test-$$
  rm -rf $_log_dir
  mkdir -p $_log_dir
  local _log_dir1=$_log_dir/$_exe1_name
  local _log_dir2=$_log_dir/$_exe2_name
  mkdir -p $_log_dir1 $_log_dir2
  
  export PKG_CONFIG_PATH=~/proj/rebuild/tests/test_data/pkg_config/dependency_tests

  test_list_all $_exe1 $_log_dir1/test_list_all
  test_list_all $_exe2 $_log_dir2/test_list_all

  test_print_requires $_exe1 $_log_dir1/test_print_requires
  test_print_requires $_exe2 $_log_dir2/test_print_requires
  
  echo "$_log_dir1 $_log_dir2"
  return 0
}

main "${@}"
_exit_code=$?
exit $_exit_code
