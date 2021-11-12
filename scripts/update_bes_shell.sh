#!/bin/bash

set -e

function main()
{
  source $(_this_dir_update_bes_bash)/../bes_bash/bes_bash.bash

  local _here="$(pwd)"
  local _my_address=$(git remote -v | awk '{ print $2; }'  | head -1)
  local _local_branch="master"
  local _address="git@gitlab.com:rebuilder/bes_shell.git"
  local _remote_branch="master"
  local _revision="@latest@"
  local _src_dir="bash/bes_bash_one_file"
  local _dst_dir="bes_bash"
  local _retry_with_delete="true"

  bes_git_subtree_update_with_temp_repo \
    ${_my_address} \
    ${_local_branch} \
    ${_address} \
    ${_remote_branch} \
    ${_revision} \
    "${_src_dir}" \
    "${_dst_dir}" \
    ${_retry_with_delete}

  cd ${_here}
  git pull
  
  return 0
}

function _this_dir_update_bes_bash()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
