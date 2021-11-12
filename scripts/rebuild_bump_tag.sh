#!/bin/bash

set -e

function main()
{
  local _this_dir=$(_rebuild_release_bump_tag_this_dir)
  source ${_this_dir}/../bes_bash/bes_bash.bash
  local _rebuild=${_this_dir}/../bin/rebuild.py
  local _python=$(which python3)

  ${_python} ${_rebuild} git bump_tag -v
  return 0
}

function _rebuild_release_bump_tag_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
