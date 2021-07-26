if [ -n "$_BES_TRACE" ]; then echo "rebuild_setup.sh begin"; fi

_rebuild_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

rebuild_dev()
{
  local _rebuild_root_dir="$(_rebuild_dev_root)"
  source "$(_rebuild_dev_root)/bes_shell/bes_shell.bash"
  source "$(_rebuild_dev_root)/bes_shell/bes_dev.bash"
  local _bes_root_dir="$(_bes_dev_root)"
  bes_dev_setup "${_bes_root_dir}" --light --set-path --set-python-path
  local _virtual_env_setup="${_rebuild_root_dir}/env/rebuild_venv_activate.bash"
  bes_dev_setup "${_rebuild_root_dir}" \
               --set-path \
               --set-python-path \
               --set-title \
               --venv-config "${_virtual_env_setup}" \
               --venv-activate \
               --change-dir \
               ${1+"$@"}
  return $?
}

rebuild_undev()
{
  local _rebuild_root_dir="$(_rebuild_dev_root)"
  source "$(_rebuild_dev_root)/bes_shell/bes_shell.bash"
  source "$(_rebuild_dev_root)/bes_shell/bes_dev.bash"
  bes_dev_unsetup "${_rebuild_root_dir}"
  return $?
}

if [ -n "$_BES_TRACE" ]; then echo "rebuild_setup.sh end"; fi
