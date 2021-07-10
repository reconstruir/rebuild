#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file path "begin"

# return a colon separated path without the head item
function bes_path_without_head()
{
  local _path="$*"
  local _head=${_path%%:*}
  local _without_head=${_path#*:}
  if [[ "${_without_head}" == "${_head}" ]]; then
    _without_head=""
  fi
  echo ${_without_head}
  return 0
}

# return just the head item of a colon separated path
function bes_path_head()
{
  local _path="$*"
  local _head=${_path%%:*}
  echo ${_head}
  return 0
}

# Strip rogue colon(s) from head of path
function bes_path_head_strip_colon()
{
  local _path="$*"
  local _result="${_path#:}"
  while [[ "${_result}" != "${_path}" ]]; do
    _path="${_result}"
    _result="${_path#:}"
  done
  echo "${_result}"
  return 0
}

# Strip rogue colon(s) from tail of path
function bes_path_tail_strip_colon()
{
  local _path="$*"
  local _result="${_path%:}"
  while [[ "${_result}" != "${_path}" ]]; do
    _path="${_result}"
    _result="${_path%:}"
  done
  echo "${_result}"
  return 0
}

# Strip rogue colon(s) from head and tail of path
function bes_path_strip_colon()
{
  local _path="$*"
  local _result=$(bes_path_head_strip_colon "${_path}")
  echo $(bes_path_tail_strip_colon "${_result}")
  return 0
}

# Strip rogue slashes from a path
function bes_path_clean_rogue_slashes()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_path_clean_rogue_slashes path"
    return 1
  fi
  local _path="${1}"
  echo "${_path}" | sed 's#//*#/#g'
  return 0
}

# remove duplicates from a path
# from https://unix.stackexchange.com/questions/14895/duplicate-entries-in-path-a-problem
function bes_path_dedup()
{
  bes_log_trace_function path $*

  if [[ $# != 1 ]]; then
    echo "Usage: bes_path_dedup path"
    return 1
  fi
  local _tmp="$*"
  local _head
  local _result=""
  while [[ -n "$_tmp" ]]; do
    _head=$(bes_path_head "${_tmp}")
    _tmp=$(bes_path_without_head "${_tmp}")
    case ":${_result}:" in
      *":${_head}:"*) :;; # already there
      *) _result="${_result}:${_head}";;
    esac
  done
  echo $(bes_path_strip_colon "${_result}")
  return 0
}

# sanitize a path by deduping entries and stripping leading or trailing colons
function bes_path_sanitize()
{
  if [[ $# -ne 1 ]]; then
    echo "Usage: bes_path_sanitize path"
    return 1
  fi
  local _path="${1}"
  local _r1="$(bes_path_clean_rogue_slashes "${_path}")"
  local _r2="$(bes_path_dedup "${_r1}")"
  local _r3="$(bes_path_strip_colon "${_r2}")"
  echo ${_r3}
  return 0
}

# remove one or more items from a colon delimited path
function bes_path_remove()
{
  bes_log_trace_function path $*

  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_remove path p1 p2 ... pN"
    return 1
  fi
  local _tmp="$1"
  shift
  local _head
  local _result=""
  while [[ -n "$_tmp" ]]; do
    _head=$(bes_path_head "${_tmp}")
    _tmp=$(bes_path_without_head "${_tmp}")
    if ! bes_is_in_list "$_head" "$@"; then
      if [[ -z ${_result} ]]; then
        _result="${_head}"
      else
        _result="${_result}:${_head}"
      fi
    fi
  done
  echo "${_result}"
  return 0
}

# append one or more items to a colon delimited path
function bes_path_append()
{
  bes_log_trace_function path $*

  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_prepend path p1 p2 ... pN"
    return 1
  fi
  local _left
  IFS=':' read -ra _left <<< "${1}"
  shift
  local _right=()
  local i
  for ((i = 1; i <= ${#}; i++)); do
    _right+=("${!i}")
  done
  local _new_path=()
  for ((i = 0; i < ${#_left[@]}; i++)); do
    _new_path+=("${_left[${i}]}")
  done
  for ((i = 0; i < ${#_right[@]}; i++)); do
    _new_path+=("${_right[${i}]}")
  done
  local _result=$(for ((i = 0; i < ${#_new_path[@]}; i++)); do
    if [[ $i != 0 ]]; then
       printf ":"
    fi
    printf "%s" "${_new_path[${i}]}"
  done)
  bes_path_sanitize "${_result}"
  return 0
}

# prepend one or more items to a colon delimited path
function bes_path_prepend()
{
  bes_log_trace_function path $*

  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_prepend path p1 p2 ... pN"
    return 1
  fi
  bes_log path debug "bes_path_prepend ARGS $*"
  bes_log path debug "bes_path_prepend NUM ${#}"
  local _right
  IFS=':' read -ra _right <<< "${1}"
  bes_log path debug "bes_path_prepend _right=${_right[*]} num=${#_right[*]}"
  shift
  local _left=()
  local i
  bes_log path debug "bes_path_prepend num args ${#}"
  for ((i = 1; i <= ${#}; i++)); do
    _left+=("${!i}")
  done
  bes_log path debug "bes_path_prepend _left=${_left[*]} num=${#_left[*]}"
  local _new_path=()
  for ((i = 0; i < ${#_left[@]}; i++)); do
    _new_path+=("${_left[${i}]}")
  done
  for ((i = 0; i < ${#_right[@]}; i++)); do
    _new_path+=("${_right[${i}]}")
  done
  local _result=$(for ((i = 0; i < ${#_new_path[@]}; i++)); do
    if [[ $i -ne 0 ]]; then
       printf ":"
    fi
    printf "%s" "${_new_path[${i}]}"
  done)
  bes_path_sanitize "${_result}"
  return 0
}

# pretty print a path one item per line including unexpanding ~/
function bes_path_print()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_path_print path"
    return 1
  fi
  local _tmp="$*"
  local _head
  while [[ -n "$_tmp" ]]; do
    _head=$(bes_path_head "${_tmp}")
    _tmp=$(bes_path_without_head "${_tmp}")
    echo ${_head/$HOME/\~}
  done
  return 0
}

function bes_env_path_sanitize()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  local _value=$(bes_var_get ${_var_name})
  local _new_value=$(bes_path_sanitize "$_value")
  bes_var_set ${_var_name} "$_new_value"
  return 0
}

function bes_env_path_append()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  shift
  local _value=$(bes_var_get ${_var_name})
  local _new_value=$(bes_path_append "${_value}" "${@}")
  bes_var_set ${_var_name} "$_new_value"
  export ${_var_name}
  return 0
}

function bes_env_path_prepend()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  shift
  bes_log path debug "bes_env_path_prepend _var_name=${_var_name}"
  local _value=$(bes_var_get ${_var_name})
  bes_log path debug "bes_env_path_prepend _value=${_value}"
  local _new_value=$(bes_path_prepend "${_value}" "${@}")
  bes_var_set ${_var_name} "$_new_value"
  export ${_var_name}
  bes_log path debug "bes_env_path_prepend result ${_new_value}"
  return 0
}

function bes_env_path_remove()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  shift
  local _parts="$@"
  local _value=$(bes_var_get ${_var_name})
  local _new_value=$(bes_path_remove "$_value" "$_parts")
  bes_var_set ${_var_name} "$_new_value"
  export ${_var_name}
  return 0
}

function bes_env_path_clear()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  bes_var_set ${_var_name} ""
  export ${_var_name}
  return 0
}

function bes_env_path_print()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  local _value=$(bes_var_get ${_var_name})
  bes_path_print $_value
  return 0
}

function _bes_variable_map_macos()
{
  local _var_name=$1
  local _rv
  case ${_var_name} in
    LD_LIBRARY_PATH)
      _rv=DYLD_LIBRARY_PATH
      ;;
    *)
      _rv=${_var_name}
      ;;
  esac
  echo ${_rv}
  return 0
}

function _bes_variable_map_linux()
{
  local _var_name=$1
  local _rv
  case ${_var_name} in
    DYLD_LIBRARY_PATH)
      _rv=LD_LIBRARY_PATH
      ;;
    *)
      _rv=${_var_name}
      ;;
  esac
  echo ${_rv}
  return 0
}

function bes_variable_map()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_variable_map var_name"
    return 1
  fi
  local _uname=$(${_BES_UNAME})
  local _var_name=$1
  local _rv
  case ${_uname} in
    Darwin)
      _rv=$(_bes_variable_map_macos ${_var_name})
      ;;
    Linux|*)
      _rv=$(_bes_variable_map_linux ${_var_name})
      ;;
  esac
  echo ${_rv}
  return 0
}

function LD_LIBRARY_PATH_var_name()
{
  local _uname=$(${_BES_UNAME})
  local _rv=
  case ${_uname} in
    Darwin)
      _rv=DYLD_LIBRARY_PATH
      ;;
    Linux|*)
      _rv=LD_LIBRARY_PATH
      ;;
  esac
  echo $_rv
  return 0
}

# Return 0 if the given path is absolute
function bes_path_is_abs()
{
  if [[ $# != 1 ]]; then
    echo "usage: bes_path_is_abs path"
    return 1
  fi
  local _path="${1}"

  if [[ "${_path}" =~ ^\/.* ]]; then
    return 0
  fi
  return 1
}

# Return 0 if the given path is a symlink
function bes_path_is_symlink()
{
  if [[ $# != 1 ]]; then
    echo "usage: bes_path_is_symlink path"
    return 1
  fi
  local _path="${1}"

  if test -h "${_path}"; then
    return 0
  fi
  return 1
}

bes_log_trace_file path "end"
