#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

function _bes_trace() ( if [[ "$_BES_TRACE" == "1" ]]; then printf '_BES_TRACE: %s\n' "$*"; fi )
function _bes_trace_function() ( _bes_trace "func: ${FUNCNAME[1]}($*)" )
function _bes_trace_file() ( _bes_trace "file: ${BASH_SOURCE}: $*" )

_bes_trace_file "begin"

_BES_LOG_FILE=$(tty)

function bes_log()
{
  if [[ $# < 3 ]]; then
    echo "Usage: bes_log component level <message>"
    return 1
  fi
  local _component=${1}
  shift
  local _level=${1}
  shift
  if ! bes_log_level_matches ${_component} ${_level}; then
    return 0
  fi
  local _timestamp=$(date +"%Y_%m_%d-%H:%M:%S-%Z")
  local _pid="$$"
  local _label="${_component}.${_level}"
  local _text=$(printf "${_timestamp} [${_pid}] (${_label}) %s\n" "$*")
  if [[ -z "${_BES_LOG_FILE}" ]]; then
    echo "${_text}"
  else
    echo "${_text}" > ${_BES_LOG_FILE}
  fi
  return 0
}

function bes_log_level_set()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_log_level_set component error|warning|info|debug|trace"
    return 1
  fi
  local _component=${1}
  local _level=${2}
  _bes_log_level_check bes_log_level_set ${_level}
  local _var_name="_BES_LOG_CONFIG_${_component}"
  bes_var_set ${_var_name} ${_level}
}

function bes_log_level_get()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_log_level_get component"
    return 1
  fi
  local _component=${1}
  local _var_name="_BES_LOG_CONFIG_${_component}"
  local _level="$(bes_var_get ${_var_name})"
  if [[ -z "${_level}" ]]; then
    _level=error
  fi
  echo ${_level}
  return 0
}

function bes_log_level_matches()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_log_level_matches component error|warning|info|debug|trace"
    return 1
  fi
  local _component=${1}
  local _level=${2}
  _bes_log_level_check bes_log_level_matches ${_level}
  local _current_level=$(bes_log_level_get ${_component})
  case "${_current_level}" in
    error)
      case "${_level}" in
        error)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    warning)
      case "${_level}" in
        error|warning)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    info)
      case "${_level}" in
        error|warning|info)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    debug)
      case "${_level}" in
        error|warning|info|debug)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    trace)
      return 0
      ;;
  esac
  return 1
}

function bes_log_config()
{
  local _items=(${@})
  local _item
  for _item in "${_items[@]}"; do
    local _component=$(echo ${_item} | awk -F"=" '{ print $1; }')
    local _level=$(echo ${_item} | awk -F"=" '{ print $2; }')
    if [[ -z "${_level}" ]]; then
      _level=error
    fi
    bes_log_level_set ${_component} ${_level}
  done
}

function _bes_log_level_is_valid()
{
  if [[ $# != 1 ]]; then
    echo "Usage: _bes_log_level_is_valid level"
    return 1
  fi
  local _level=${1}
  case "${_level}" in
    error|warning|info|debug|trace)
      return 0
      ;;
    *)
      ;;
  esac
  return 1
}

function _bes_log_level_check()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_log_level_is_valid label level"
    return 1
  fi
  local _label=${1}
  local _level=${2}
  if ! _bes_log_level_is_valid ${_level}; then
    echo "$_label: Invalid log level: ${_level}.  Should be one of error|warning|info|debug|trace"
    exit 1
  fi
  return 0
}

if [[ -n ${BES_LOG} ]]; then
  bes_log_config "${BES_LOG}"
fi

function bes_log_trace_function()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_log_trace_function component"
    return 1
  fi
  local _component=${1}
  shift
  bes_log ${_component} trace "${FUNCNAME[1]}($*)"
}

function bes_log_trace_file()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_log_trace_function component"
    return 1
  fi
  local _component=${1}
  shift
  bes_log ${_component} trace "${BASH_SOURCE}: ($*)"
}

function bes_log_set_log_file()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_log_set_log_file log_file"
    return 1
  fi
  local _log_file="${1}"
  _BES_LOG_FILE="${_log_file}"
  return 0
}

#_bes_trace_function() ( _bes_trace "func: ${FUNCNAME[1]}($*)" )
#function _bes_trace_file() ( _bes_trace "file: ${BASH_SOURCE}: $*" )

_bes_trace_file "end"
