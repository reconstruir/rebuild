#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to download stuff

_bes_trace_file "begin"

# Download a url to a file with optional username and password.
# uses curl or wget dependning on which one is found
function bes_download()
{
  if [[ $# < 2 ]]; then
    bes_message "Usage: bes_download url filename <username> <password>"
    return 1
  fi
  local _url="${1}"
  shift
  local _filename="${1}"
  shift
  local _username
  local _password
  if [[ $# > 0 ]]; then
    shift
    _username="${1}"
  fi
  if [[ $# > 0 ]]; then
    shift
    _password="${1}"
  fi
  local _dirname="$(dirname ${_filename})"
  mkdir -p ${_dirname}
  local _rv

  if $(bes_has_program curl); then
    _bes_download_curl "${_url}" "${_filename}" "${_username}" "${_password}"
    _rv=$?
    return ${_rv}
  fi
  
  if $(bes_has_program wget); then
    _bes_download_wget "${_url}" "${_filename}" "${_username}" "${_password}"
    _rv=$?
    return ${_rv}
  fi

  bes_message "bes_download: no curl or wget found."
  
  return 1
}

function _bes_download_curl()
{
  if [[ $# < 4 ]]; then
    bes_message "Usage: _bes_download_curl url filename <username> <password>"
    return 1
  fi
  local _url="${1}"
  local _filename="${2}"
  local _username="${3}"
  local _password="${4}"
  local _auth_args
  if [[ -n "${_username}" && -n "${_password}" ]]; then
    _auth_args="--user ${_username}:${_password}"
  else
    _auth_args=""
  fi
  local _http_code=$(curl ${_auth_args} ${_url} --location --output ${_filename} -w "%{http_code}\n" 2> /dev/null)
  if [[ "${_http_code}" != "200" ]]; then
    return 1
  fi
  return 0
}

function _bes_download_wget()
{
  if [[ $# < 4 ]]; then
    bes_message "Usage: _bes_download_wget url filename <username> <password>"
    return 1
  fi
  local _url="${1}"
  local _filename="${2}"
  local _username="${3}"
  local _password="${4}"
  local _auth_args
  if [[ -n "${_username}" && -n "${_password}" ]]; then
    _auth_args="--user ${_username} --password ${_password}"
  else
    _auth_args=""
  fi

  # FIXME: need more error checking here
  wget --quiet --user ${_auth_args} ${_url} -O ${_filename}
  if [[ -f ${_filename} ]]; then
    return 0
  fi
  return 1
}

_bes_trace_file "end"
