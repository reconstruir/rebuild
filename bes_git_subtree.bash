#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

_bes_trace_file "begin"

# Update a git subtree in a temporary cloned dir to prevent polluting the local
# repo with the subtree remote including tags which confuses things. Foo.
function bes_git_subtree_update_with_temp_repo()
{
  if [[ $# != 8 ]]; then
    bes_message "usage: bes_git_subtree_update_with_temp_repo my_address local_branch address remote_branch revision src_dir dst_dir retry_with_delete"
    return 2
  fi
  local _my_address="${1}"
  local _local_branch=${2}
  local _remote_address=${3}
  local _remote_branch=${4}
  local _remote_revision=${5}
  local _src_dir="${6}"
  local _dst_dir="${7}"
  local _retry_with_delete=${8}
  local _remote_name=$(basename ${_remote_address} | sed 's/.git//')
  local _tmp_branch_name=tmp-split-branch-${_remote_name}
  local _my_name=$(basename ${_my_address} | sed 's/.git//')

  local _tmp_dir="${TMPDIR}/bes_git_subtree_update_tmp-${_my_name}-$$"
  if ! git clone ${_my_address} "${_tmp_dir}"; then
    bes_message "bes_git_subtree_update_with_temp_repo: Failed to clone ${_my_address}"
    return 3
  fi
  cd ${_tmp_dir}
  if ! bes_git_subtree_update \
       ${_tmp_dir} \
       ${_local_branch} \
       ${_remote_address} \
       ${_remote_branch} \
       ${_remote_revision} \
       ${_src_dir} \
       ${_dst_dir} \
       ${_retry_with_delete}; then
    bes_message "bes_git_subtree_update_with_temp_repo: Failed to update in ${_tmp_dir}"
    return 2
  fi
  if ! git push -u origin ${_local_branch}; then
    bes_message "bes_git_subtree_update_with_temp_repo: Failed to push to ${_my_address}:${_local_branch}"
    return 2
  fi
  return 0
}

function bes_git_subtree_update()
{
  if [[ $# != 8 ]]; then
    bes_message "usage: bes_git_subtree_update root_dir local_branch address remote_branch revision src_dir dst_dir retry_with_delete"
    return 2
  fi
  local _root_dir="${1}"
  local _local_branch=${2}
  local _remote_address=${3}
  local _remote_branch=${4}
  local _remote_revision=${5}
  local _src_dir="${6}"
  local _dst_dir="${7}"
  local _retry_with_delete=${8}
  local _remote_name=$(basename ${_remote_address} | sed 's/.git//')
  local _tmp_branch_name=tmp-split-branch-${_remote_name}

  if ! bes_git_is_repo "${_root_dir}"; then
    bes_message "not a git repo: ${_root_dir}"
    return 1
  fi

  # We need a clean tree with no changes
  if bes_git_repo_has_uncommitted_changes "${_root_dir}"; then
    bes_message "not clean - uncommitted changes: ${_root_dir}"
    return 1
  fi
  
  bes_debug_message "updating ${_dst_dir} with ${_remote_address}/${_src_dir}@${_remote_revision}"

  if [[ ${_remote_revision} == "@latest@" ]]; then
    _remote_revision=$(bes_git_repo_latest_tag ${_remote_address})
    bes_debug_message "using latest tag for ${_remote_address} is ${_remote_revision}"
  fi

  local _remote_commit_hash=$(bes_git_repo_commit_for_ref ${_remote_address} ${_remote_revision})
  bes_debug_message "using ${_remote_commit_hash} for ${_remote_revision}"
  
  local _current_branch=$(bes_git_call "${_root_dir}" branch | awk '{ print $2; }')
  if [[ ${_current_branch} != ${_local_branch} ]]; then
    if bes_git_repo_has_uncommitted_changes; then
      bes_message "The current branch is not ${_local_branch} and it has changes."
      return 1
    fi
    bes_git_call "${_root_dir}" checkout ${_local_branch} >& ${_BES_GIT_LOG_FILE}
  fi

  bes_debug_message "pulling origin ${_local_branch} to make sure up to date."
  bes_git_call "${_root_dir}" pull origin ${_local_branch} >& ${_BES_GIT_LOG_FILE}

  trap "_bes_subtree_at_exit_cleanup ${_root_dir} ${_remote_name} ${_tmp_branch_name}" EXIT

  if _bes_git_subtree_doit "${_root_dir}" ${_local_branch} ${_remote_address} ${_remote_branch} ${_remote_revision} ${_remote_commit_hash} ${_src_dir} ${_dst_dir} ${_remote_name} ${_tmp_branch_name}; then
    bes_message "Updated ${_root_dir} with ${_remote_address}/${_src_dir}@${_remote_revision}"
    return 0
  fi
  
  bes_message "subtree failed because of conflicts.  Hard resetting to the HEAD"

  bes_git_call "${_root_dir}" reset --hard HEAD >& ${_BES_GIT_LOG_FILE}

  if [[ ${_retry_with_delete} == "true" ]]; then
    bes_debug_message "retrying with deleting ${_dst_dir} first"
    bes_git_call "${_root_dir}" rm -rf ${_dst_dir} >& ${_BES_GIT_LOG_FILE}
    bes_git_call "${_root_dir}" commit ${_dst_dir} -m"remove ${_dst_dir} so subtree can replace it without conflicts." >& ${_BES_GIT_LOG_FILE}
    if _bes_git_subtree_doit "${_root_dir}" ${_local_branch} ${_remote_address} ${_remote_branch} ${_remote_revision} ${_remote_commit_hash} "${_src_dir}" "${_dst_dir}" ${_remote_name} ${_tmp_branch_name}; then
        bes_message "Updated ${_root_dir} with ${_remote_address}/${_src_dir}@${_remote_revision}.  Had to delete first."
        return 0
    fi
    bes_message "both subtree attempts failed.  something is very screwy"
  fi
  
  return 1
}

function _bes_git_subtree_doit()
{
  local _root_dir="${1}"
  local _local_branch=${2}
  local _remote_address=${3}
  local _remote_branch=${4}
  local _remote_revision=${5}
  local _remote_commit_hash=${6}
  local _src_dir="${7}"
  local _dst_dir="${8}"
  local _remote_name=${9}
  local _tmp_branch_name=${10}

  bes_git_remote_remove "${_root_dir}" ${_remote_name}
  
  bes_git_call "${_root_dir}" checkout ${_local_branch} >& ${_BES_GIT_LOG_FILE}
  bes_git_call "${_root_dir}" remote add -f ${_remote_name} ${_remote_address} -t ${_remote_branch} >& ${_BES_GIT_LOG_FILE} # --no-tags
  bes_debug_message "checking out ${_remote_name}/${_remote_branch}"
  bes_git_call "${_root_dir}" checkout ${_remote_name}/${_remote_branch} >& ${_BES_GIT_LOG_FILE}
  bes_debug_message "checking out ${_remote_commit_hash}"
  bes_git_call "${_root_dir}" checkout ${_remote_commit_hash} >& ${_BES_GIT_LOG_FILE}
  bes_debug_message "trying subtree split -P ${_src_dir} -b ${_tmp_branch_name}"
  bes_git_call "${_root_dir}" subtree split -P "${_src_dir}" -b ${_tmp_branch_name} >& ${_BES_GIT_LOG_FILE}
  bes_debug_message "trying checkout ${_local_branch}"
  bes_git_call "${_root_dir}" checkout ${_local_branch} >& ${_BES_GIT_LOG_FILE}

  if [[ -d "${_dst_dir}" ]]; then
    # Merge existing subtree
    command="merge"
    message="Merging ${_remote_address} ${_remote_revision} ${_src_dir} into ${_dst_dir}"
  else
    # Add subtree for first time
    command="add"
    message="Adding ${_remote_address} ${_remote_revision} ${_src_dir} into ${_dst_dir}"
  fi

  bes_debug_message "trying subtree ${command} --squash -P ${_dst_dir}"
  if ! bes_git_call "${_root_dir}" subtree ${command} --squash -P "${_dst_dir}" ${_tmp_branch_name} -m "${message}" >& ${_BES_GIT_LOG_FILE}; then
    bes_message "FAILED: subtree ${command} --squash -P ${_dst_dir}"
    _bes_subtree_at_exit_delete_tmp_branch "${_root_dir}" ${_tmp_branch_name}
    return 1
  fi
  _bes_subtree_at_exit_delete_tmp_branch "${_root_dir}" ${_tmp_branch_name}
  return 0
}

function _bes_subtree_at_exit_cleanup()
{
  local _actual_exit_code=$?
  if [[ $# != 3 ]]; then
    bes_message "usage: _bes_subtree_at_exit_cleanup root_dir remote_name tmp_branch_name"
    return 1
  fi
  local _root_dir=${1}
  local _remote_name=${2}
  local _tmp_branch_name=${3}
  bes_debug_message "_bes_subtree_at_exit_cleanup: _actual_exit_code=${_actual_exit_code} _root_dir=${_root_dir} _remote_name=${_remote_name} _tmp_branch_name=${_tmp_branch_name}"

  if [[ ! -d "${_root_dir}" ]]; then
    bes_debug_message "skipping cleanup cause _root_dir does not exist: ${_root_dir}"
    return ${_actual_exit_code}
  fi
  
  bes_git_remote_remove "${_root_dir}" ${_remote_name}
  _bes_subtree_at_exit_delete_tmp_branch "${_root_dir}" ${_tmp_branch_name}
  if [[ ${_actual_exit_code} == 0 ]]; then
    bes_debug_message "success"
  else
    bes_message "failed"
  fi
  return ${_actual_exit_code}
}

function _bes_subtree_at_exit_delete_tmp_branch()
{
  if [[ $# != 2 ]]; then
    bes_debug_message "usage: _bes_subtree_at_exit_delete_tmp_branch root tmp_branch_name"
    return 1
  fi
  local _root_dir=${1}
  local _tmp_branch_name=${2}
  if ! bes_git_local_branch_exists "${_root_dir}" ${_tmp_branch_name}; then
    bes_debug_message "no ${_tmp_branch_name} branch found to delete"
    return 0
  fi
  bes_git_call "${_root_dir}" branch -D ${_tmp_branch_name} >& ${_BES_GIT_LOG_FILE}
  bes_debug_message "deleted ${_tmp_branch_name} branch"
  return 0
}

_bes_trace_file "end"
