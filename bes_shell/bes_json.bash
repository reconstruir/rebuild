#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

_bes_trace_file "begin"

function bes_json_file_parse()
{
  if [[ $# < 1 ]]; then
    bes_message "Usage: bes_json_parse_file filename <args>"
    return 1
  fi
  local _filename="${1}"
  shift
  local _this_dir=$(echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")
  local _json_parser="${_this_dir}/dominictarr_json.sh"

  "${_json_parser}" ${1+"$@"} < "${_filename}"
  local _exit_code=$?
  return ${_exit_code}
}

function bes_json_file_get_field()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: bes_json_file_get_field filename field"
    return 1
  fi
  local _filename="${1}"
  local _field="${2}"

  bes_json_file_parse "${_filename}" -b | grep -w "${_field}" | awk -F"\t" '{ print $2; }' | tr -d '"'
  local _exit_code=$?
  return ${_exit_code}
}

_bes_trace_file "end"
