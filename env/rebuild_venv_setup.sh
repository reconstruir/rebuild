#!/bin/bash

set -e

function main()
{
  source $(_rebuild_venv_setup_this_dir)/../bes_bash/bes_bash.bash

  local _this_dir="$(_rebuild_venv_setup_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _best="$(which best.py)"
  local _python="$(bes_python_find_default)"

  ${_python} ${_best} pip_project install_requirements \
             --root-dir "${_root_dir}/VE/rebuild" \
             $@
  return 0
}

function _rebuild_venv_setup_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
