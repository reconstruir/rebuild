#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

_bes_trace_file "begin"

function _bes_python_testing_make_testing_python_exe()
{
  if [[ $# != 3 ]]; then
    bes_message "Usage: _bes_python_testing_make_testing_python_exe where basename full_version"
    return 1
  fi
  local _where="${1}"
  local _basename="${2}"
  local _full_version="${3}"
  mkdir -p ${_where}
  local _exe="${_where}/${_basename}"
  cat > "${_exe}" << EOF
#!/bin/bash
echo Python ${_full_version} 1>&2
exit 0
EOF
  chmod 755 ${_exe}
  echo "${_exe}"
  return 0
}

function _bes_python_testing_make_testing_pip_exe()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: _bes_python_testing_make_testing_pip_exe python_exe full_version"
    return 1
  fi
  local _python_exe="${1}"
  local _where="$(dirname "${_python_exe}")"
  local _python_version=$(bes_python_exe_version "${_python_exe}")
  local _full_version="${2}"
  local _pip_basename=pip${_python_version}
  local _pip_exe="${_where}/${_pip_basename}"

  cat > "${_pip_exe}" << EOF
#!/usr/bin/env python
print('"pip ${_full_version} from /doesnt/matter (python ${_python_version})"')
raise SystemExit(0)
EOF
  chmod 755 ${_pip_exe}
  echo "${_pip_exe}"
  return 0
}

_bes_trace_file "end"
