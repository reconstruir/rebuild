#!/bin/bash

set -e

function main()
{
  source $(_this_dir_update_bes_shell)/../bes_shell/bes_all.bash

  local _root_dir="$(pwd)"
  local _local_branch="master"
  local _address="git@gitlab.com:rebuilder/bes_shell.git"
  local _remote_branch="master"
  local _revision="@latest@"
  local _src_dir="bash/bes_shell"
  local _dst_dir="bes_shell"
  local _retry_with_delete="true"

  bes_git_subtree_update \
    ${_root_dir} \
    ${_local_branch} \
    ${_address} \
    ${_remote_branch} \
    ${_revision} \
    "${_src_dir}" \
    "${_dst_dir}" \
    ${_retry_with_delete}
  
  return 0
}

function _this_dir_update_bes_shell()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
