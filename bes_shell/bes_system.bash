#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file system "begin"

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
_BES_BASENAME_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} basename)
_BES_CAT_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} cat)
_BES_DIRNAME_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} dirname)
_BES_GREP_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} grep)
_BES_MKDIR_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} mkdir)
_BES_PWD_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} pwd)
_BES_TR_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} tr)
_BES_UNAME=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} uname)

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

function bes_system_info()
{
  local _uname=$(${_BES_UNAME})
  local _system='unknown'
  local _arch=$(${_BES_UNAME} -m)
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

function _bes_windows_version()
{
  local _version=$(cmd /c ver | grep "Microsoft Windows \[Version" | tr '[' ' ' | tr ']' ' ' | awk '{ print $4; }')
  echo ${_version}
  return 0
}

bes_log_trace_file system "end"
