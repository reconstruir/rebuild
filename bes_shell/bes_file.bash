#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file path "begin"

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

# print the normalized dir
function bes_dir_normalize()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_dir_normalize dir"
    return 1
  fi
  local _dir="${1}"
  if [[ ! -e "${_dir}" ]]; then
    bes_message "bes_dir_normalize: Directory not found: ${_dir}"
    return 0
  fi
  if [[ ! -d "${_dir}" ]]; then
    bes_message "bes_dir_normalize: Not a directory: ${_dir}"
    return 0
  fi
  local _normalized_dir="$(command cd -P "${_dir}" > /dev/null && command pwd -P )"
  echo "${_normalized_dir}"
  return 0
}

# Determine the normalized directory for a file taking symlinks into account.
function bes_file_dir()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_file_dir filename"
    return 1
  fi
  local _filename="${1}"
  local _resolved_filename
  if [[ -h "${_filename}" ]]; then
    _resolved_filename="$(command readlink "${_filename}" )"
  else
    _resolved_filename="${_filename}"
  fi
  local _file_dir="${_resolved_filename%/*}"
  if [[ "${_file_dir}" == "${_resolved_filename}" ]]; then
    _file_dir=.
  fi
  local _normalized_file_dir="$(bes_dir_normalize "${_file_dir}")"
  echo "${_normalized_file_dir}"
  return 0
}

# check that a file exists or print a message
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

bes_log_trace_file path "end"
