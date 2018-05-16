# Mostly borrowed from https://unwiredcouch.com/2016/04/13/bash-unit-testing-101.html

# Print all the unit tests defined in this script environment (functions starting with test_)
function bes_testing_print_unit_tests()
{
  local _result
  declare -a _result
  i=$(( 0 ))
  for unit_test in $(declare -f | grep -o "^test_[a-zA-Z_0-9]*"); do
    _result[$i]=$unit_test
    i=$(( $i + 1 ))
  done
  echo ${_result[*]}
  return 0
}

_bes_testing_exit_code=0

# Run all the unit tests found in this script environment
function bes_testing_run_unit_tests()
{
  local _tests=$(bes_testing_print_unit_tests)
  local _test
  local _rv
  for _test in $_tests; do
    ${_test}
  done
  exit $_bes_testing_exit_code
}

# Run that an expression argument is true and print that
function bes_assert()
{
  eval "${1}"
  if [[ $? -ne 0 ]]; then
    echo "${FUNCNAME[1]}: failed: " ${1}
    _bes_testing_exit_code=1
   else
     echo "${FUNCNAME[1]}: passed"
  fi
}
