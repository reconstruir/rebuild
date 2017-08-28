_rebuild_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

rebuild_dev()
{
  bes_dev
  bes_setup $(_rebuild_dev_root) ${1+"$@"}
  return 0
}
