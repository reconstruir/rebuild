#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Unit testing code mostly borrowed from:
#   https://unwiredcouch.com/2016/04/13/bash-unit-testing-101.html

# Print all the unit tests defined in this script environment (functions starting with test_)
function bes_testing_print_unit_tests()
{
  if [[ ${BES_UNIT_TEST_LIST} ]]; then
    echo "${BES_UNIT_TEST_LIST}"
    return 0
  fi
  local _result
  declare -a _result
  i=$(( 0 ))
  for unit_test in $(declare -f | ${_BES_GREP_EXE} -o "^test_[a-zA-Z_0-9]*"); do
    _result[$i]=$unit_test
    i=$(( $i + 1 ))
  done
  echo ${_result[*]}
  return 0
}

# Call a function and print the exit code
function bes_testing_call_function()
{
  local _function=${1}
  shift
  ${_function} ${1+"$@"}
  local _rv=$?
  echo ${_rv}
  return 0
}

function _bes_testing_exit_code_filename()
{
  local _exit_code_filename="${TMPDIR}/_bes_testing_exit_code_$$"
  echo "${_exit_code_filename}"
  return 0
}

function _bes_testing_exit_code_filename_clean()
{
  local _exit_code_filename="$(_bes_testing_exit_code_filename)"
  rm -f "${_exit_code_filename}"
  return 0
}

function _bes_testing_exit_code_set()
{
  local _exit_code_filename="$(_bes_testing_exit_code_filename)"
  echo $1 > "${_exit_code_filename}"
  echo set ${_exit_code_filename} to 1
  return 0
}

function _bes_testing_exit_code_get()
{
  local _exit_code_filename="$(_bes_testing_exit_code_filename)"
  local _exit_code=0
  if [[ -f "${_exit_code_filename}" ]]; then
    _exit_code=$(cat "${_exit_code_filename}")
  fi
  echo ${_exit_code}
  return $(expr ${_exit_code})
}

# Run all the unit tests found in this script environment
function bes_testing_run_unit_tests()
{
  local _tests=$(bes_testing_print_unit_tests)
  local _test
  local _rv
  for _test in $_tests; do
    ${_test}
  done
  local _exit_code="$(_bes_testing_exit_code_get)"
  _bes_testing_exit_code_filename_clean
  exit ${_exit_code}
}

# Run that an expression argument is true and print that
function bes_assert()
{
  local _filename=$($_BES_BASENAME_EXE ${BASH_SOURCE[1]})
  local _line=${BASH_LINENO[0]}
  local _function=${FUNCNAME[1]}
  eval "${1}"
  if [[ $? -ne 0 ]]; then
    echo "failed: ${_function} $_filename:$_line: " ${1}
    if [[ -n ${BES_UNIT_TEST_FAIL} ]]; then
        exit 1
    fi
    _bes_testing_exit_code_set 1
  else
    echo "$_filename $_function: passed"
  fi
}

# Make a temp dir for testing
function bes_testing_make_temp_dir()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_testing_make_temp_dir label"
    return 1
  fi
  local _label="${1}"
  local _pid=$$
  local _basename="${_label}_${_pid}"
  local _tmpdir="${TMPDIR}/${_basename}"
  mkdir -p "${_tmpdir}"
  local _normalized_tmpdir="$(command cd -P "${_tmpdir}" > /dev/null && command pwd -P )"
  echo "${_normalized_tmpdir}"
  return 0
}

# Return 0 if the content of a file matches content
function bes_testing_check_file()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_testing_check_file filename content"
    return 1
  fi
  local _filename="${1}"
  local _content="${2}"
  echo "${_content}" | "${_BES_DIFF}" "${_filename}" - >& /dev/null
  local _rv=$?
  if [[ ${_rv} != 0 ]]; then
    echo "${_content}" | "${_BES_DIFF}" "${_filename}" -
  fi
  return ${_rv}
}
