if [ -n "$_BES_TRACE" ]; then echo "rebuild_setup.sh begin"; fi

_rebuild_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

source "$(_rebuild_dev_root)/bes_shell/bes_shell.sh"

rebuild_dev()
{
  local _root_dir="$(_rebuild_dev_root)"
  local _virtual_env_setup="${_root_dir}/env/rebuild_venv_activate.bash"
  bes_setup_v2 "${_root_dir}" \
               --set-path \
               --set-python-path \
               --set-title \
               --venv-config "${_virtual_env_setup}" \
               --venv-activate \
               --change-dir \
               ${1+"$@"}
  return 0
}

rebuild_undev()
{
  local _root_dir=$(_rebuild_dev_root)
  bes_unsetup ${_root_dir}
  return 0
}

if [ -n "$_BES_TRACE" ]; then echo "rebuild_setup.sh end"; fi
