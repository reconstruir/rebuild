#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to deal with brew on macos

_bes_trace_file "begin"

# Return 0 if this macos has brew
function bes_has_brew()
{
  local _system=$(bes_system)
  if [[ ${_system} != "macos" ]]; then
    bes_message "bes_has_brew: this only works on macos"
    return 1
  fi
  if bes_has_program brew; then
    return 0
  fi
  return 1
}

# Install brew
function bes_brew_install()
{
  local _system=$(bes_system)
  if [[ ${_system} != "macos" ]]; then
    bes_message "bes_brew_install: this only works on macos"
    return 1
  fi
  if bes_has_brew; then
    return 0
  fi
  return 1
}

_bes_trace_file "end"
