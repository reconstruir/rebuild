_rebuild_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

rebuild_dev()
{
  bes_dev no
  source ~/.rebuild/rebuild_deps/setup.sh
  rebuild_deps_setup
  local _system_path=$(bes_system_path)
  export BESTEST_UNIXPATH=~/.rebuild/rebuild_deps/${_system_path}/stuff/bin
  export BESTEST_PYTHONPATH=~/.rebuild/rebuild_deps/${_system_path}/stuff/lib/python
  bes_setup $(_rebuild_dev_root) ${1+"$@"}
  return 0
}

rebuild_undev()
{
  rebuild_deps_unsetup
  unset BESTEST_UNIXPATH BESTEST_PYTHONPATH
  bes_unsetup $(_rebuild_dev_root)
  return 0
}
