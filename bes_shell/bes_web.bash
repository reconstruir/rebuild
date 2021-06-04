#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to do web requests stuff

_bes_trace_file "begin"

# Download a url to a file with optional username and password.
# uses curl or wget dependning on which one is found
function bes_web_request()
{
  if [[ $# < 1 ]]; then
    bes_message "Usage: bes_web_request url --data key=value --username username --password password --headers-file file"
    return 1
  fi
  local _url="${1}"
  shift
  local _username
  local _password
  local _datas=()
  local _headers=()
  local _headers_file=
  local _response_data_file=
  local _http_status_file=
  local _method=
  local _log_file=/dev/null
  local _enable_redirects=false
  local _positional_args=()
  local _key
  while [[ $# -gt 0 ]]; do
    _key="${1}"
    bes_debug_message "bes_web_request: checking key ${_key} ${2}"
    case ${_key} in
      --username)
        _username="${2}"
        shift # past argument
        shift # past value
        ;;
      --password)
        _password="${2}"
        shift # past argument
        shift # past value
        ;;
      --data)
        _datas+=( "${2}" )
        shift # past argument
        shift # past value
        ;;
      --header)
        _headers+=( "${2}" )
        shift # past argument
        shift # past value
        ;;
      --headers-file)
        _headers_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --response-data-file)
        _response_data_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --http-status-file)
        _http_status_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --method)
        _method="${2}"
        shift # past argument
        shift # past value
        ;;
      --log-file)
        _log_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --enable-redirects)
        _enable_redirects=true
        shift # past argument
        ;;
      *)    # unknown option
        positional_args+=("${1}") # save it in an array for later
        shift # past argument
        ;;
    esac
  done
  
  bes_debug_message "             _datas: ${_datas[@]}"
  bes_debug_message "           _headers: ${_headers[@]}"
  bes_debug_message "      _headers_file: ${_headers_file}"
  bes_debug_message "            _method: ${_method}"
  bes_debug_message "  _http_status_file: ${_http_status_file}"
  bes_debug_message "          _log_file: ${_log_file}"
  bes_debug_message "          _password: ${_password}"
  bes_debug_message "          _username: ${_username}"
  bes_debug_message "_response_data_file: ${_response_data_file}"
  bes_debug_message "  _enable_redirects: ${_enable_redirects}"
  
  set -- "${positional_args[@]}" # restore positional parameters

  if [[ -n "${_username}" ]] && [[ -z "${_password}" ]]; then
    bes_message "bes_web_request: If username is given then password needs to be given too."
    return 1
  fi

  if [[ -n "${_password}" ]] && [[ -z "${_username}" ]]; then
    bes_message "bes_web_request: If password is given then username needs to be given too."
    return 1
  fi
  
  local _rv
  if $(bes_has_program curl); then
    local _curl_args=()
    if [[ -n "${_username}" ]]; then
      _curl_args+=( "--user" "${_username}:${_password}" )
    fi
    local _data
    for _data in "${_datas[@]}"; do
      _curl_args+=( "--data" "${_data}" )
    done
    local _header
    for _header in "${_headers[@]}"; do
      _curl_args+=( "--header" "${_header}" )
    done
    if [[ -n "${_headers_file}" ]]; then
      _curl_args+=( "--header" "@${_headers_file}" )
    fi
    if [[ -n "${_method}" ]]; then
      _curl_args+=( "--request" "${_method}" )
    fi
    if [[ ${_enable_redirects} == "true" ]]; then
      _curl_args+=( "--location" )
    fi
    _bes_web_request_curl "${_url}" "${_response_data_file}" "${_http_status_file}" "${_log_file}" "${_curl_args[@]}"
    _rv=$?
    return ${_rv}
  fi
  
  if $(bes_has_program wget); then
    local _wget_args=()
    if [[ -n "${_username}" ]]; then
      _wget_args+=( "--user" "${_username}" )
      _wget_args+=( "--password" "${_password}" )
    fi
    local _data
    for _data in "${_datas[@]}"; do
      _wget_args+=( "--post-data"="${_data}" )
    done
    local _header
    for _header in "${_headers[@]}"; do
      _wget_args+=( "--header"="${_header}" )
    done
    _bes_web_request_wget "${_url}" "${_response_data_file}" "${_http_status_file}" "${_log_file}" "${_wget_args[@]}"
    _rv=$?
    return ${_rv}
  fi

  bes_message "bes_web_request: no curl or wget found."
  
  return 1
}

function _bes_web_request_curl()
{
  if [[ $# < 4 ]]; then
    bes_message "Usage: _bes_web_request_curl url response_data_file http_status_file log_file <extra_args>"
    return 1
  fi
  local _url="${1}"
  shift
  local _response_data_file="${1}"
  shift
  local _http_status_file="${1}"
  shift
  local _log_file="${1}"
  shift
  local _extra_args=(${1+"$@"})
  local _http_status_args=""
  local _args=()

  _args+=( "--silent" )
  if [[ -n "${_http_status_file}" ]]; then
    _args+=( "--write-out" "%{http_code}\n" )
  fi
  if [[ -n "${_response_data_file}" ]]; then
    _args+=( "--output" "${_response_data_file}" )
  fi

  local _arg
  for _arg in "${_extra_args[@]}"; do
    _args+=( "${_arg}" )
  done
    
  _args+=( "${_url}" )
  bes_debug_message "_bes_web_request_curl: calling: curl ${_args[@]}"
  local _curl_output=$(curl ${_args[@]} 2> "${_log_file}")
  local _curl_exit_code=$?
  if [[ -n "${_http_status_file}" ]]; then
    echo ${_curl_output} > "${_http_status_file}"
  fi
  return ${_curl_exit_code}
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
