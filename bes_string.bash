#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to deal with strings

bes_log_trace_file path "begin"

# Strip whitespace from the head of a string
# From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
function bes_str_strip_head()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_strip_head str"
    return 1
  fi
  local _str="${1}"
  local _stripped="$(echo -e "${_str}" | sed -e 's/^[[:space:]]*//')"
  echo "${_stripped}"
  return 0
}

# Strip whitespace from the tail of a string
# From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
function bes_str_strip_tail()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_strip_head str"
    return 1
  fi
  local _str="${1}"
  local _stripped="$(echo -e "${_str}" | sed -e 's/[[:space:]]*$//')"
  echo "${_stripped}"
  return 0
}

# Strip whitespace from both the head and tail of a string
# From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
function bes_str_strip()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_strip_head str"
    return 1
  fi
  local _str="${1}"
  local _stripped="$(echo -e "${_str}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  echo "${_stripped}"
  return 0
}

# Partition a string into left, separator and right.
# delimiter needs to be single char
# the result is 3 lines:
#  left
#  delimiter
#  right
# if no delimiter is found then the result is:
#  str
#
#
# you can either use "head" and "tail" on the results to get the parts you
# need or use arrays like this:
# foo=( "$(bes_str_partition "  key: value with spaces" ":")" )
function bes_str_partition()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: bes_str_partition str delimiter"
    return 1
  fi
  local _str="${1}"
  local _delimiter=${2}
  if [[ ${#_delimiter} != 1 ]]; then
    bes_message "bes_str_partition: delimiter should be a single char: \"${_delimiter}\""
    return 1
  fi
  local _left="$(echo "${_str}" | cut -d${_delimiter} -f 1)"
  local _right
  local _delimiter_result
  if [[ "${_left}" != "${_str}" ]]; then
    local _left_len=$(echo ${#_left})
    local _cut_index=$(( _left_len + 2 ))
    _right="$(echo "${_str}" | cut -b${_cut_index}-)"
    _delimiter_result=${_delimiter}
  fi

  echo "${_left}"
  echo "${_delimiter_result}"
  echo "${_right}"
  
  return 0
}

# Convert a single argument string to lower case
function bes_str_to_lower()
{
  local _result=$( echo "$@" | $_BES_TR_EXE '[:upper:]' '[:lower:]' )
  echo ${_result}
  return 0
}

function bes_str_split()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_str_split string delimiter"
    return 1
  fi
  local _string="${1}"
  local _delimiter="${2}"
  local _saveIFS="${IFS}"
  local _result
  IFS="${_delimiter}" read -r -a _result <<< "${_string}"
  echo "${_result[@]}"
  IFS="${_saveIFS}"
  return 0
}

# return 0 if str is an integer
function bes_str_is_integer()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_str_is_integer str"
    return 1
  fi
  local _str="${1}"
  local _pattern='^[0-9]+$'
  if [[ ${_str} =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

# return 0 if str starts with head
function bes_str_starts_with()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_starts_with str head"
    return 1
  fi
  local _str="${1}"
  local _head="${2}"
  local _pattern="^${_head}.*$"
  if [[ "${_str}" =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

# return 0 if str ends with tail
function bes_str_ends_with()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_ends_with str tail"
    return 1
  fi
  local _str="${1}"
  local _tail="${2}"
  local _pattern="^.*${_tail}$"
  if [[ "${_str}" =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

# Remove head from str
function bes_str_remove_head()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_remove_head str head"
    return 1
  fi
  local _str="${1}"
  local _head="${2}"
  echo ${_str#${_head}}
  return 0
}

# Remove tail from str
function bes_str_remove_tail()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_remove_tail str tail"
    return 1
  fi
  local _str="${1}"
  local _tail="${2}"
  echo ${_str%${_tail}}
  return 0
}

# return 0 if str is an integer
function bes_str_is_integer()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_str_is_integer str"
    return 1
  fi
  local _str="${1}"
  local _pattern='^[0-9]+$'
  if [[ ${_str} =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

bes_log_trace_file path "end"
