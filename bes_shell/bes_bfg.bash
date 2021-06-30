#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to call bfg

_bes_trace_file "begin"

function bes_bfg_call()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: version"
    return 1
  fi
  if ! $(bes_has_program java); then
    bes_message "java not f.ound"
    return 1
  fi
  local _version="${1}"
  shift
  local _local_jar="${HOME}/.besbfg/bfg/bfg-${_version}.jar"
  _bfg_download ${_version} "${_local_jar}"
  bes_message "calling: java -jar ${_local_jar} "${1+"$@"}
  java -jar ${_local_jar} ${1+"$@"}
  local _rv=$?
  return ${_rv}
}

function _bfg_download()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: _bfg_download version local_jar"
    return 1
  fi
  local _version="${1}"
  local _local_jar="${2}"
  local _version="${1}"
  shift
  
  if [[ ! -f ${_local_jar} ]]; then
    local _url="https://repo1.maven.org/maven2/com/madgag/bfg/${_version}/bfg-${_version}.jar"
    bes_download "${_url}" "${_local_jar}"
  fi
  if [[ ! -f ${_local_jar} ]]; then
    bes_message "failed to download: ${_url} to ${_local_jar}"
    return 1
  fi

  local _actual_version=$(bfg_version ${_local_jar})
  if [[ ${_actual_version} != ${_version} ]]; then
    bes_message "version mismatch error.  should be ${_version} instead of ${_actual_version}"
    return 1
  fi
  
  return 0
}

function bfg_version()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bfg_jar"
    return 1
  fi
  local _bfg_jar="${1}"
  local _version=$(java -jar ${_bfg_jar} --version | awk '{ print $2; }')
  echo ${_version}
  return 0
}

_bes_trace_file "end"
