function _rebuild_venv_activate_main()
{
  source $(_rebuild_venv_activate_this_dir)/../bes_bash/bes_bash.bash

  local _this_dir="$(_rebuild_venv_activate_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _bes_root_dir=$(_bes_dev_root)
  local _requirements=(
    "${_bes_root_dir}/bes_requirements.txt"
    "${_bes_root_dir}/bes_requirements_dev.txt"
    "${_root_dir}/rebuild_requirements.txt"
    "${_root_dir}/rebuild_requirements_dev.txt"
  )

  if bes_pip_project_requirements_are_stale "${_root_dir}/VE/rebuild" ${_requirements[@]}; then
    ${_this_dir}/rebuild_venv_setup.sh ${_requirements[@]}
  fi
  
  echo "${_root_dir}/VE/rebuild/bin/activate"
  return 0
}

function _rebuild_venv_activate_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

source $(_rebuild_venv_activate_main ${1+"$@"})
unset -f _rebuild_venv_activate_main
unset -f _rebuild_venv_activate_this_dir
