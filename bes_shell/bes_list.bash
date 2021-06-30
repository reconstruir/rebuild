#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file list "begin"

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

bes_log_trace_file path "end"
