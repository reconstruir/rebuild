#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

function _bes_trace() ( if [[ "$_BES_TRACE" == "1" ]]; then printf '_BES_TRACE: %s\n' "$*"; fi )
function _bes_trace_function() ( _bes_trace "func: ${FUNCNAME[1]}($*)" )
function _bes_trace_file() ( _bes_trace "file: ${BASH_SOURCE}: $*" )

_bes_trace_file "begin"

# A basic UNIX path that is guranteed to find common exeutables on all platforms
_BES_BASIC_PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/sbin:/usr/bin:/bin:/c/Windows/System32

# An implemention of "which" with the same semantics as /usr/bin/which for cases
# where /usr/bin/which is not found
function _bes_which()
{
  function _bes_which_help()
  {
    echo "_bes_which: illegal option -- ${_key}"
    echo "usage: _bes_which [-as] program ..."
  }
  
  local _positional_args=()
  local _key
  local _list_all_instances=false
  local _no_output=false
  while [[ $# -gt 0 ]]; do
    _key="${1}"
    case ${_key} in
      -a)
        _list_all_instances=true
        shift # past argument
        ;;
      -s)
        _no_output=true
        shift # past argument
        ;;
      -*)
        _bes_which_help
        return 1
        ;;
      *)    # unknown option
        positional_args+=("${1}") # save it in an array for later
        shift # past argument
        ;;
    esac
  done

  set -- "${positional_args[@]}" # restore positional parameters
  
  if [[ $# < 1 ]]; then
    _bes_which_help
    return 1
  fi

  local _programs
  declare -a _programs
  _programs=( ${1+"$@"} )
  local _one_whiches
  declare -a _one_whiches
  local _one_rv
  local _found_all=true
  local _one_which

  for _program in "${_programs[@]}"; do
    _one_whiches=( $(_bes_which_one_program "${_program}" ${_list_all_instances}) )
    _one_rv=$?
    if [[ ${_one_rv} == 0 ]]; then
      if [[ ${_no_output} == "false" ]]; then
        for _one_which in "${_one_whiches[@]}"; do
          echo "${_one_which}"
        done
      fi
    else
      _found_all=false
    fi
  done

  if [[ ${_found_all} == "true" ]]; then
    return 0
  fi
  return 1
}

function _bes_which_one_program()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_which_one_program program list_all"
    return 1
  fi
  local _program="${1}"
  local _list_all=${2}
  local _path
  declare -a _path
  local _path_entry
  local _possible_which
  local _found_any=false

  if [[ -x "${_program}" ]]; then
    echo "${_program}"
    return 0
  fi
  
  IFS=':' read -ra _path <<< "${PATH}"
  for _path_entry in "${_path[@]}"; do
    _possible_which=${_path_entry}/${_program}
    if [[ -x "${_possible_which}" ]]; then
      echo "${_possible_which}"
      if [[ ${_list_all} != "true" ]]; then
        return 0
      fi
      _found_any=true
    fi
  done
  if [[ ${_found_any} == "true" ]]; then
    return 0
  fi
  return 1
}

# When found which is in the same place on both linux and macos
# when not found use the handrolled _bes_which instead
if [[ -x /usr/bin/which ]]; then
  _BES_WHICH_EXE=/usr/bin/which
else
  _BES_WHICH_EXE=_bes_which
fi


# Use which to find the abs paths to a handful of executables used in this library.
# The reason for using _BES_BASIC_PATH in this manner is that we want this library to
# work *even* if the callers PATH is empty or "bad"
_BES_AWK_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} awk)
_BES_TR_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} tr)
_BES_BASENAME_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} basename)
_BES_DIRNAME_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} dirname)
_BES_GREP_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} grep)
_BES_CAT_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} cat)
_BES_PWD_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} pwd)
_BES_MKDIR_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} mkdir)

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

# remove duplicates from a path
# from https://unix.stackexchange.com/questions/14895/duplicate-entries-in-path-a-problem
function bes_path_dedup()
{
  _bes_trace_function $*
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
  local _path=$(bes_path_dedup "$1")
  echo $(bes_path_strip_colon "${_path}")
  return 0
}

# remove one or more items from a colon delimited path
function bes_path_remove()
{
  _bes_trace_function $*
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
  _bes_trace_function $*
  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_append path p1 p2 ... pN"
    return 1
  fi
  local path="$1"
  shift
  local what
  local result="${path}"
  while [[ $# > 0 ]]; do
    what="$1"
    result=$(bes_path_remove "${result}" "${what}")
    result="${result}":"${what}"
    shift
  done
  result=$(bes_path_sanitize "${result}")
  echo "${result}"
  return 0
}

# prepend one or more items to a colon delimited path
function bes_path_prepend()
{
  _bes_trace_function $*
  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_prepend path p1 p2 ... pN"
    return 1
  fi
  local _path="$1"
  shift
  local _what
  local _result="${_path}"
  while [[ $# > 0 ]]; do
    _what="$1"
    _result="${_what}":"${_result}"
    shift
  done
  echo $(bes_path_sanitize "${_result}")
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
  _bes_trace_function $*
  local _var_name=$(bes_variable_map $1)
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_sanitize "$_value")
  bes_var_set $_var_name "$_new_value"
  return 0
}

function bes_env_path_append()
{
  _bes_trace_function $*
  local _var_name=$(bes_variable_map $1)
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_append "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_prepend()
{
  _bes_trace_function $*
  local _var_name=$(bes_variable_map $1)
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_prepend "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_remove()
{
  _bes_trace_function $*
  local _var_name=$(bes_variable_map $1)
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_remove "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_clear()
{
  _bes_trace_function $*
  local _var_name=$(bes_variable_map $1)
  bes_var_set $_var_name ""
  export $_var_name
  return 0
}

function bes_env_path_print()
{
  _bes_trace_function $*
  local _var_name=$(bes_variable_map $1)
  local _value=$(bes_var_get $_var_name)
  bes_path_print $_value
  return 0
}

# Source a shell file if it exists
function bes_source()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_source filename\n\n"
    return 1
  fi
  local _filename=$1
  if [[ -f $_filename ]]; then
     source $_filename
     return 0
  fi
  return 1
}

# Source all the *.sh files in a dir if it exists and has such files
function bes_source_dir()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_source_dir dir\n\n"
    return 1
  fi
  local _dir=$1
  if [[ ! -d $_dir ]]; then
    return 0
  fi
  local _files=$(find $_dir -maxdepth 1 -name "*.sh")
  local _file
  for _file in $_files; do
    source "$_file"
  done
  return 0
}

# Convert a single argument string to lower case
function bes_to_lower()
{
  local _result=$( echo "$@" | $_BES_TR_EXE '[:upper:]' '[:lower:]' )
  echo ${_result}
  return 0
}

# Return an exit code of 0 if the argument is "true."  true is one of: true, 1, t, yes, y
function bes_is_true()
{
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_is_true what\n\n"
    return 1
  fi
  local _what=$(bes_to_lower "$1")
  local _rv
  case "${_what}" in
    true|1|t|y|yes)
      _rv=0
      ;;
    *)
      _rv=1
      ;;
  esac
  return ${_rv}
}

# Return 0 if the first argument is in any of the following arguments
function bes_is_in_list()
{
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_is_in_list what l1 l2 ... lN\n\n"
    return 1
  fi
  local _what="$1"
  shift
  local _next
  while [[ $# > 0 ]]; do
    _next="$1"
    if [[ "$_what" == "$_next" ]]; then
      return 0
    fi
    shift
  done
  return 1
}

function bes_setup()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_setup root_dir [go_there]\n\n"
    return 1
  fi
  local _root_dir=$1
  local _go_there=true
  if [[ $# > 1 ]]; then
    _go_there=$2
  fi

  bes_env_path_prepend PATH ${_root_dir}/bin
  bes_env_path_prepend PYTHONPATH ${_root_dir}/lib

  if $(bes_is_true $_go_there); then
    cd $_root_dir
    bes_tab_title $($_BES_BASENAME_EXE $_root_dir)
  fi
  
  return 0
}

function bes_unsetup()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_unsetup root_dir\n\n"
    return 1
  fi
  local _root_dir=$1
  bes_env_path_remove PATH ${_root_dir}/bin
  bes_env_path_remove PYTHONPATH ${_root_dir}/lib
  bes_tab_title ""
  return 0
}

function bes_setup_v2()
{
  _bes_trace_function $*

  local _root_dir
  local _set_title
  local _change_dir
  local _set_path
  local _set_pythonpath
  local _virtual_env=
  local _positional_args=()
  local _key
  while [[ $# -gt 0 ]]; do
    _key="${1}"
    bes_debug_message "bes_setup_v2: checking key ${_key} ${2}"
    case ${_key} in
      --virtual-env)
        _virtual_env="${2}"
        shift # past argument
        shift # past value
        ;;
      --set-path)
        _set_path=true
        shift # past argument
        ;;
      --set-python-path)
        _set_python_path=true
        shift # past argument
        ;;
      --change-dir)
        _change_dir=true
        shift # past argument
        ;;
      --set-title)
        _set_title=true
        shift # past argument
        ;;
      *)    # unknown option
        positional_args+=("${1}") # save it in an array for later
        shift # past argument
        ;;
    esac
  done
  
  set -- "${positional_args[@]}" # restore positional parameters

  if [[ $# != 1 ]]; then
    printf "\nUsage: bes_setup <options> root_dir\n\n"
    return 1
  fi
  local _root_dir="${1}"

  if [[ ${_set_path} == true ]]; then
    bes_env_path_prepend PATH "${_root_dir}/bin"
  fi
  if [[ ${_set_python_path} == true ]]; then
    bes_env_path_prepend PYTHONPATH "${_root_dir}/lib"
  fi
  if [[ ${_change_dir} == true ]]; then
    cd "${_root_dir}"
  fi
  if [[ ${_set_title} == true ]]; then
    bes_tab_title $($_BES_BASENAME_EXE "${_root_dir}")
  fi

  return 0
}

# Get a var value
function bes_var_get()
{
  eval 'printf "%s\n" "${'"$1"'}"'
}

# Set a var value
function bes_var_set()
{
  eval "$1=\"\$2\""
}

# Unset a var value
function bes_var_unset()
{
  eval "unset $1"
}

# Export a var value
function bes_var_export()
{
  eval "export $1=\"\$2\""
}

function bes_PATH()
{
  bes_env_path_print PATH
}

function bes_PYTHONPATH()
{
  bes_env_path_print PYTHONPATH
}

function bes_LD_LIBRARY_PATH()
{
  bes_env_path_print LD_LIBRARY_PATH
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
  local _system=$(bes_system)
  local _var_name=$1
  local _rv
  case ${_system} in
    macos)
      _rv=$(_bes_variable_map_macos ${_var_name})
      ;;
    linux|*)
      _rv=$(_bes_variable_map_linux ${_var_name})
      ;;
  esac
  echo ${_rv}
  return 0
}

function LD_LIBRARY_PATH_var_name()
{
  local _system=$(bes_system)
  local _rv=
  case ${_system} in
    macos)
      _rv=DYLD_LIBRARY_PATH
      ;;
    linux|*)
      _rv=LD_LIBRARY_PATH
      ;;
  esac
  echo $_rv
  return 0
}

function bes_tab_title()
{
  echo -ne "\033]0;"$*"\007"
  local _prompt=$(echo -ne "\033]0;"$*"\007")
  export PROMPT_COMMAND='${_prompt}'
}

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
  local _filename=$($_BES_BASENAME_EXE ${BASH_SOURCE[1]})
  local _line=${BASH_LINENO[0]}
  local _function=${FUNCNAME[1]}
  
  eval "${1}"
  if [[ $? -ne 0 ]]; then
    echo "failed: ${_function} $_filename:$_line: " ${1}
    if [[ -n ${BES_UNIT_TEST_FAIL} ]]; then
        exit 1
    fi
    _bes_testing_exit_code=1
  else
    echo "$_filename $_function: passed"
  fi
}

function _bes_windows_version()
{
  local _version=$(cmd /c ver | grep "Microsoft Windows \[Version" | tr '[' ' ' | tr ']' ' ' | awk '{ print $4; }')
  echo ${_version}
  return 0
}

function bes_system_info()
{
  local _uname_exe=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} uname)
  local _uname=$(${_uname_exe})
  local _system='unknown'
  local _arch=$(${_uname_exe} -m)
  local _distro=
  local _major=
  local _minor=
  local _path=
  local _version=
  case "${_uname}" in
    Darwin)
      _system='macos'
      _version=$(/usr/bin/sw_vers -productVersion)
      _major=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $1; }')
      _minor=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $2; }')
      _path=${_system}-${_major}/${_arch}
      ;;
	  Linux)
      _system='linux'
      _version=$(${_BES_CAT_EXE} /etc/os-release | ${_BES_GREP_EXE} VERSION_ID= | ${_BES_AWK_EXE} -F"=" '{ print $2; }' | ${_BES_AWK_EXE} -F"." '{ printf("%s.%s\n", $1, $2); }' | ${_BES_TR_EXE} -d '\"')
      _major=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $1; }')
      _minor=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $2; }')
      _distro=$(${_BES_CAT_EXE} /etc/os-release | ${_BES_GREP_EXE} -e '^ID=' | ${_BES_AWK_EXE} -F"=" '{ print $2; }')
      _path=${_system}-${_distro}-${_major}/${_arch}
      ;;
    MINGW64_NT*) # git bash
      _system="windows"
      _distro="mingw64"
      ;;
    MSYS_NT*) # msys2
      _system="windows"
      _distro="msys2"
      ;;
	esac

  if [[ ${_system} == "windows" ]]; then
    local _powershell=/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
    local _version=$(${_powershell} [System.Environment]::OSVersion | ${_BES_GREP_EXE} Win32NT | ${_BES_AWK_EXE} '{ print $2; }')
    local _major=$(echo ${_version} | ${_BES_AWK_EXE} -F'.' '{ print $1 }')
    local _minor=$(echo ${_version} | ${_BES_AWK_EXE} -F'.' '{ print $2 }')
    _path=${_system}-${_major}/${_arch}
  fi
  echo ${_system}:${_distro}:${_major}:${_minor}:${_arch}:${_path}
  return 0
}

function bes_system()
{
  local _path=$(bes_system_info | ${_BES_AWK_EXE} -F":" '{ print $1 }')
  echo ${_path}
  return 0
}

function bes_system_path()
{
  local _path=$(bes_system_info | ${_BES_AWK_EXE} -F":" '{ print $6 }')
  echo ${_path}
  return 0
}

function bes_script_name()
{
  if [[ -n "${_BES_SCRIPT_NAME}"  ]]; then
    echo "${_BES_SCRIPT_NAME}"
    return 0
  fi
  if [[ ${0} =~ .+bash$ ]]; then
    echo "bes_shell"
    return 0
  fi
  echo $(basename "${0}")
  return 0
}

function bes_message()
{
  local _script_name=$(bes_script_name)
  echo ${_script_name}: ${1+"$@"}
  return 0
}

function bes_debug_message()
{
  if [[ -z "${BES_DEBUG}" ]]; then
    return 0
  fi
  local _output=""
  if [[ -n "${BES_LOG_FILE}" ]]; then
    _output="${BES_LOG_FILE}"
  else
    if [[ -t 1 ]]; then
      _output=$(tty)
    fi
  fi
  local _script_name=$(bes_script_name)
  local _pid=$$
  local _message=$(printf "%s(%s): %s\n" ${_script_name} ${_pid} ${1+"$@"})
  if [[ -n "${_output}" ]]; then
    echo ${_message} >> ${_output}
  else
    echo ${_message}
  fi
  return 0
}

function bes_is_ci()
{
  if [[ -n "${CI}"|| -n "${HUDSON_COOKIE}" ]]; then
    return 0
  fi
  return 1
}

function bes_console_message()
{
  if bes_is_ci ; then
    BES_DEBUG=1 bes_debug_message ${1+"$@"}
  else    
    BES_DEBUG=1 BES_LOG_FILE=$(tty) bes_debug_message ${1+"$@"}
  fi
  return $?
}

function _bes_checksum_text_macos()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_text_macos algorithm text"
    return 1
  fi
  local _algorithm="${1}"
  local _text="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(echo "${_text}" | md5)
      ;;
    sha1)
      _result=$(echo "${_text}" | shasum -a 1 | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(echo "${_text}" | shasum -a 256 | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(echo "${_text}" | shasum -a 512 | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

function _bes_checksum_file_macos()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_file_macos algorithm filename"
    return 1
  fi
  local _algorithm="${1}"
  local _filename="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(md5 -q "${_filename}")
      ;;
    sha1)
      _result=$(shasum -a 1 "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(shasum -a 256 "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(shasum -a 512 "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

function _bes_checksum_file_linux()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_file_linux algorithm filename"
    return 1
  fi
  local _algorithm="${1}"
  local _filename="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(md5sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha1)
      _result=$(sha1sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(sha256sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(sha512sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

function _bes_checksum_text_linux()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_text_linux algorithm text"
    return 1
  fi
  local _algorithm="${1}"
  local _text="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(echo "${_text}" | md5sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha1)
      _result=$(echo "${_text}" | sha1sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(echo "${_text}" | sha256sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(echo "${_text}" | sha512sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

# Checksum file using algorithm
function bes_checksum_file()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_checksum_file algorithm filename"
    return 1
  fi
  local _algorithm="${1}"
  local _filename="${2}"
  local _system=$(bes_system)
  local _result
  local _rv
  case "${_system}" in
    linux|windows)
      _result=$(_bes_checksum_file_linux ${_algorithm}  "${_filename}")
      _rv=$?
      ;;
    macos)
      _result=$(_bes_checksum_file_macos ${_algorithm}  "${_filename}")
      _rv=$?
      ;;
    *)
      echo "unknown system: ${_system}"
      return 1
      ;;
  esac
  echo ${_result}
  return ${_rv}
}

# Checksum text using algorithm
function bes_checksum_text()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_checksum_text algorithm text"
    return 1
  fi
  local _algorithm="${1}"
  local _text="${2}"
  local _system=$(bes_system)
  local _result
  local _rv
  case "${_system}" in
    linux|windows)
      _result=$(_bes_checksum_text_linux ${_algorithm}  "${_text}")
      _rv=$?
      ;;
    macos)
      _result=$(_bes_checksum_text_macos ${_algorithm}  "${_text}")
      _rv=$?
      ;;
    *)
      echo "unknown system: ${_system}"
      return 1
      ;;
  esac
  echo ${_result}
  return ${_rv}
}

# Checksum only the files in a directory.  Empty directories are ignored.
function bes_checksum_dir_files()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_checksum_dir_files algorithm dir"
    return 1
  fi
  local _algorithm="${1}"
  local _dir="${2}"
  local _file
  local _checksum
  local _checksums=$(cd ${_dir} && find . -type f -print0 | while read -d $'\0' _file; do
    _checksum=$(bes_checksum_file ${_algorithm} "${_file}")
    printf "%s %s\n" "${_file}" "${_checksum}" | $_BES_TR_EXE ' ' '_'
  done | sort)
  local _result=$(bes_checksum_text ${_algorithm} "${_checksums}")
  echo ${_result}
  return 0
}

# Checksum a manifest of files
function bes_checksum_manifest()
{
  if [[ $# != 3 ]]; then
    echo "Usage: bes_checksum_manifest algorithm dir manifest"
    return 1
  fi
  local _algorithm="${1}"
  local _dir="${2}"
  local _manifest="${3}"
  if [[ ! -f "${_manifest}" ]]; then
    echo "bes_checksum_manifest: manifest not found: ${_manifest}"
    return 1
  fi
  local _file
  local _checksum
  local _saveIFS="${IFS}"
  IFS=''
  local _checksums=$(while read _file; do
    _checksum=$(bes_checksum_file ${_algorithm} "${_dir}/${_file}")
    printf "%s %s\n" "${_file}" "${_checksum}" | $_BES_TR_EXE ' ' '_'
  done < "${_manifest}" | sort)
  IFS="${_saveIFS}"
  local _result=$(bes_checksum_text ${_algorithm} "${_checksums}")
  echo ${_result}
  return 0
}

function bes_function_exists()
{
  local _name=${1}
  local _type=$(type -t ${_name})
  if [[ "${_type}" == "function" ]]; then
    return 0
  else
    return 1
  fi
}

function _bes_function_invoke()
{
  _bes_trace_function $*
  if [[ $# < 2 ]]; then
    printf "\nUsage: _bes_function_invoke function default_rv args\n\n"
    return 1
  fi
  local _function=${1}
  shift
  local _default_rv=${1}
  shift
  local _rv=${_default_rv}
  if bes_function_exists ${_function}; then
    eval ${_function} ${1+"$@"}
    _rv=$?
  fi
  return ${_rv}
}

# invoke a function if it exists.  returns exit code of function or 1 if the function does not exist.
function bes_function_invoke()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_function_invoke_if function args\n\n"
    return 1
  fi
  local _function=${1}
  shift
  _bes_function_invoke ${_function} 1 ${1+"$@"}
  local _rv=$?
  return ${_rv}
}

# invoke a function if it exists.  returns exit code of function or 0 if the function does not exist.
function bes_function_invoke_if()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_function_invoke_if function args\n\n"
    return 1
  fi
  local _function=${1}
  shift
  _bes_function_invoke ${_function} 0 ${1+"$@"}
  local _rv=$?
  return ${_rv}
}

# FIXME: retire this one
function bes_invoke()
{
  bes_function_invoke_if ${1+"$@"}
}

function bes_has_program()
{
  local _program="$1"
  $(${_BES_WHICH_EXE} "${_program}" >& /dev/null)
  local _rv=$?
  return ${_rv}
}

function bes_find_program()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_find_program env_var_name prog_name1 [ prog_name1 ... prog_nameN ]"
    return 1
  fi
  local _env_var_name=${1}
  shift
  local _exe=$(bes_var_get ${_env_var_name})
  if [[ -n ${_exe} ]]; then
    if ! $(bes_has_program ${_exe}); then
      echo ""
      return 1
    fi
    echo "${_exe}"
    return 0  
  fi
  for _exe in "$@"; do
    if bes_has_program ${_exe}; then
      echo ${_exe}
      return 0
    fi
  done
  echo ""
  return 1
}

# atexit function suitable for trapping and printing the exit code
# trap "bes_atexit_message_successful ${_remote_name}" EXIT
function bes_atexit_message_successful()
{
  local _actual_exit_code=$?
  if [[ ${_actual_exit_code} == 0 ]]; then
    bes_message success ${1+"$@"}
  else
    bes_message failed ${1+"$@"}
  fi
  return ${_actual_exit_code}
}

function bes_atexit_remove_dir_handler()
{
  local _actual_exit_code=$?
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_atexit_remove_dir_handler dir"
    return 1
  fi
  local _dir="${1}"
  if [[ -e "${_dir}" ]]; then
    if [[ ! -d "${_dir}" ]]; then
      bes_message "_bes_atexit_remove_dir_handler: not a directory: ${_dir}"
      return 1
    fi
    bes_debug_message "_bes_atexit_remove_dir_handler: removing ${_dir}"
    /bin/rm -rf ${_dir}
  else
    bes_debug_message "_bes_atexit_remove_dir_handler: directory not found ${_dir}"
  fi
  return ${_actual_exit_code}
}

# DEPRECATED: use bes_abs_dir instead
# Return the absolute path for the path arg
function bes_abs_path()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_abs_path path"
    return 1
  fi
  local _path="${1}"
  echo $(cd ${_path} && pwd)
  return 0
}

# Return the absolute dir path for path.  Note that path will be created
# if it doesnt exist so that this function can be used for paths that
# dont yet exist.  That is useful for scripts that want to normalize
# their file input/output arguments.
function bes_abs_dir()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_abs_dir path"
    return 1
  fi
  local _path="${1}"
  if [[ ! -d "${_path}" ]]; then
    $_BES_MKDIR_EXE -p "${_path}"
  fi
  local _result="$(cd "${_path}" && $_BES_PWD_EXE)"
  echo ${_result}
  return 0
}

function bes_abs_file()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_abs_file filename"
    return 1
  fi
  local _filename="${1}"
  local _dirname="$($_BES_DIRNAME_EXE "${_filename}")"
  local _basename="$($_BES_BASENAME_EXE "${_filename}")"
  local _abs_dirname="$(bes_abs_dir "${_dirname}")"
  local _result="${_abs_dirname}"/"${_basename}"
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

# return just the extension of a file
function bes_file_extension()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_file_extension filename"
    return 1
  fi
  local _filename="${1}"
  local _base=$($_BES_BASENAME_EXE -- "${_filename}")
  local _ext="${_base##*.}"
  echo "${_ext}"
  return 0
}

# print the file size in bytes
function bes_file_size()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_file_size filename"
    return 1
  fi
  local _filename="${1}"
  local _file_size=$(wc -c < "${_filename}" | tr -d ' ')
  echo "${_file_size}"
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

function bes_question_yes_no()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_question_yes_no var_name message"
    return 1
  fi
  local _CHOICES="[y]es [n]o"
  local _var_name="${1}"
  local _message="${2}"
  local _local_answer
  local _result=1
  while true; do
    read -p "${_message} - ${_CHOICES}: " _local_answer
    case "${_local_answer}" in
      y|Y|yes|YES)
        _result=yes
        break
        ;;
      n|N|no|NO)
        _result=no
        break
        ;;
      *)
        bes_message "Invalid answer: ${_local_answer}.  Please answer: ${_CHOICES}"
    esac
  done
  eval ${_var_name}=${_result}
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

function bes_file_check()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_file_check label"
    return 1
  fi
  local _label=${FUNCNAME[1]}
  local _filename="${1}"
  if [[ ! -e "${_filename}" ]]; then
    bes_message "${_label}: not found: ${_filename}"
    exit 1
  fi
  return 0
}

_bes_trace_file "end"
