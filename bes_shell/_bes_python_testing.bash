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

_bes_trace_file "end"
