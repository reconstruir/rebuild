#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file path "begin"

# return just the extension of a file
function bes_filename_extension()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_filename_extension filename"
    return 1
  fi
  local _filename="${1}"
  local _base=$($_BES_BASENAME_EXE -- "${_filename}")
  local _ext="${_base##*.}"
  echo "${_ext}"
  return 0
}

bes_log_trace_file path "end"
