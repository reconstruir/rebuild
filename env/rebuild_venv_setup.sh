#!/bin/bash

set -e

function main()
{
  source $(_this_dir_rebuild_venv_setup)/../bes_bash/bes_bash.bash

  local _this_dir="$(_this_dir_rebuild_venv_setup)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _rebuild="${_root_dir}/bin/reb.py"
  local _projects_root_dir="${_root_dir}/VE"
  local _requirements="${_root_dir}/requirements.txt"
  local _requirements_dev="${_root_dir}/requirements-dev.txt"

  PYTHONPATH=${_root_dir}/lib:${PYTHONPATH}
  ${_rebuild} pip_project install_requirements --root-dir "${_projects_root_dir}" rebuild "${_requirements}"
  ${_rebuild} pip_project install_requirements --root-dir "${_projects_root_dir}" rebuild "${_requirements_dev}"
  
  return 0
}

function _this_dir_rebuild_venv_setup()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
