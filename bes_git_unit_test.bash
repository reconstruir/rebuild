#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

_bes_trace_file "begin"

_BES_GIT_LOG_FILE=${BES_GIT_LOG_FILE:-/dev/null}

# Add a file to repo with filename and content and optional push (false by default)
function _bes_git_add_file()
{
  if [[ $# < 3 ]]; then
    echo "usage: _bes_git_add_file repo filename content [push]"
    return 1
  fi
  local _repo="${1}"
  shift
  local _filename="${1}"
  shift
  local _content="${1}"
  shift
  local _push=false
  if [[ $# > 0 ]]; then
    _push=${1}
  fi
  local _dirname=$(dirname "${_filename}")
  (
    cd ${_repo} && \
    mkdir -p ${_dirname} && \
    echo "${_content}" > ${_filename} && \
    ${BES_GIT_EXE:-git} add ${_filename} && \
    ${BES_GIT_EXE:-git} commit -m"add ${_filename}" ${_filename} && \
    if [[ "${_push}" == "true" ]]; then ${BES_GIT_EXE:-git} push origin master; fi
  ) >& "${_BES_GIT_LOG_FILE}"

  return 0
}

function _bes_git_add_lfs_file()
{
  if [[ $# != 3 ]]; then
    bes_message "usage: _bes_git_add_lfs_file repo filename content"
    return 1
  fi
  local _repo="${1}"
  local _filename="${2}"
  local _content="${3}"
  
  local _ext=$(bes_file_extension "${_filename}")
  ( cd ${_repo} && \
      ${BES_GIT_EXE:-git} lfs install && \
      echo "*.${_ext} filter=lfs diff=lfs merge=lfs -text" > .gitattributes && \
      ${BES_GIT_EXE:-git} add .gitattributes && \
      ${BES_GIT_EXE:-git} commit -m"add attributes" .gitattributes && \
      echo "${_content}" > "${_filename}" && \
      ${BES_GIT_EXE:-git} add "${_filename}" && \
      ${BES_GIT_EXE:-git} commit -m"add ${_filename}" "${_filename}"
  ) >& "${_BES_GIT_LOG_FILE}"
}

function _bes_git_make_temp_repo()
{
  if [[ $# != 1 ]]; then
    echo "usage: bes_git_make_temp_repo name"
    return 1
  fi
  local _name="${1}"
  local _tmp=/tmp/temp_git_repo_${_name}_$$
  local _tmp_remote_repo=${_tmp}/remote
  mkdir -p ${_tmp_remote_repo}
  ( bes_git_call "${_tmp_remote_repo}" init --bare --shared ) >& "${_BES_GIT_LOG_FILE}"
  local _tmp_local_repo=${_tmp}/local
  ( bes_git_call "${_tmp}" clone ${_tmp_remote_repo} local ) >& "${_BES_GIT_LOG_FILE}"
  _bes_git_add_file ${_tmp_local_repo} readme.txt "this is readme.txt\n" true
  echo ${_tmp}
  if [[ -n "${BES_DEBUG}" ]]; then
    bes_console_message "temp git repo for ${_name} => ${_tmp}"
  fi
  return 0
}

function _bes_git_temp_repo_rm()
{
  if [[ $# != 1 ]]; then
    echo "usage: _bes_git_temp_repo_rm where"
    return 1
  fi
  local _where="${1}"
  if [[ -n "${BES_DEBUG}" ]]; then
    return 0
  fi
  rm -rf ${_where}
  return 0
}

function _bes_git_check_num_args()
{
  if [[ $# != 3 ]]; then
    bes_message "ERROR: _bes_git_check_num_args got ${#} instead of 3 args."
    exit 1
  fi
  local _msg="${1}"
  local _expected="${2}"
  local _actual="${3}"
  if [[ ${_expected} != ${_actual} ]]; then
    bes_message "expecting ${_exepected} instead of ${_actual} num args: ${_msg}"
    exit 1
  fi
}  

function _bes_git_test_address_name()
{
  _bes_git_check_num_args "_bes_git_test_address_name" 1 $#
  local _address=${1}
  local _name=$( echo ${_address}  | awk -F"/" '{ print $NF; }'  | sed 's/\.git//')
  echo ${_name}
  return 0
}

# Clone a repo to a tmp dir
function _bes_git_test_clone()
{
  _bes_git_check_num_args "_bes_git_test_clone" 1 $#
  local _address=${1}
  local _name=$(_bes_git_test_address_name ${_address})
  local _tmp=/tmp/temp_git_repo_${_name}_$$
  ${BES_GIT_EXE:-git} clone ${_address} ${_tmp} >& "${_BES_GIT_LOG_FILE}"
  echo ${_tmp}
  return 0
}

_bes_trace_file "end"
