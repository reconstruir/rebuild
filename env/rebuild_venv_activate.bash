function _rebuild_venv_print_activate_script()
{
  source $(_rebuild_this_dir_venv_activate)/../bes_shell/bes_all.bash
  
  local _this_dir="$(_rebuild_this_dir_venv_activate)"
  local _root_dir="$(bes_abs_path ${_this_dir}/..)"
  local _rebuild="${_root_dir}/bin/reb.py"
  local _projects_root_dir="${_root_dir}/VE"
  local _requirements="${_root_dir}/requirements.txt"

  ${_this_dir}/rebuild_venv_setup.sh
  local _activate_script=$(PYTHONPATH=${_root_dir}/lib:${PYTHONPATH} ${_rebuild} pip_project activate_script --root-dir "${_projects_root_dir}" rebuild)
  echo "${_activate_script}"
  
  return 0
}

function _rebuild_venv_print_pythonpath()
{
  source $(_rebuild_this_dir_venv_activate)/../bes_shell/bes_all.bash

  local _this_dir="$(_rebuild_this_dir_venv_activate)"
  local _root_dir="$(bes_abs_path ${_this_dir}/..)"
  local _lib_dir="$(bes_abs_dir ${_root_dir}/lib)"
  echo export PYTHONPATH="${PYTHONPATH}:/${_lib_dir}"
  
  return 0
}

function _rebuild_venv_print_path()
{
  source $(_rebuild_this_dir_venv_activate)/../bes_shell/bes_all.bash

  local _this_dir="$(_rebuild_this_dir_venv_activate)"
  local _root_dir="$(bes_abs_path ${_this_dir}/..)"
  local _bin_dir="$(bes_abs_dir ${_root_dir}/bin)"
  echo export PATH="${_bin_dir}:${PATH}"
  
  return 0
}

function _rebuild_this_dir_venv_activate()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}
source $(_rebuild_venv_print_activate_script ${1+"$@"})
eval $(_rebuild_venv_print_pythonpath)
# FIXME: this breaks when there are spaces in path
#eval $(_rebuild_venv_print_path)
unset -f _rebuild_venv_print_activate_script
unset -f _rebuild_venv_print_pythonpath
unset -f _rebuild_venv_print_path
unset -f _rebuild_this_dir_venv_activate
