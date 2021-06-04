#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

_bes_trace_file "begin"

# Call pipenv with a specific root
function bes_devenv_ensure()
{
  if [[ $# != 4 ]]; then
    echo "usage: bes_pipenv_ensure python_exe project_dir pip_version pipenv_version"
    return 1
  fi
  local _python_exe="${1}"
  local _project_dir="${2}"
  local _pip_version=${3}
  local _pipenv_version=${4}

  if ! bes_pipenv_ensure "${_python_exe}" "${_project_dir}" "${_pip_version}" "${_pipenv_version}"; then
    bes_message "bes_devenv_ensure: failed to ensure devenv in ${_project_dir} with ${_python_exe}"
    return 1
  fi
  
  return 0
}

_bes_trace_file "end"
