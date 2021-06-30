#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to deal with python

_bes_trace_file "begin"

# Return 0 if the python version given is found
function bes_has_python()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_has_python version"
    return 1
  fi
  local _version=${1}
  local _python_exe=python${_version}
  if bes_has_program ${_python_exe}; then
    return 0
  fi
  return 1
}

# Print the full version $major.$minor.$revision of a python executable
function bes_python_exe_full_version()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_exe_full_version exe"
    return 1
  fi
  local _exe="${1}"
  if [[ ! -x ${_exe} ]]; then
    bes_message "bes_python_exe_full_version: problem executing python: ${_exe}"
    return 1
  fi
  local _full_version=$(${_exe} --version 2>&1 | ${_BES_AWK_EXE} '{ print $2; }')
  echo "${_full_version}"
  return 0
}

# Print the $major.$minor version of a python executable
function bes_python_exe_version()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_exe_version exe"
    return 1
  fi
  local _exe="${1}"
  if [[ ! -x ${_exe} ]]; then
    bes_message "bes_python_exe_version: problem executing python: ${_exe}"
    return 1
  fi
  local _full_version=$(bes_python_exe_full_version "${_exe}")
  local _version=$(echo ${_full_version} | ${_BES_AWK_EXE} -F'.' '{ printf("%s.%s\n", $1, $2); }')
  echo "${_version}"
  return 0
}

# Install the given python version or do nothing if already installed
function bes_python_install()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_install version"
    return 1
  fi
  local _version=${1}
  if bes_has_python ${_version}; then
    return 0
  fi
  local _system=$(bes_system)
  local _rv=1
  case ${_system} in
    macos)
      _bes_python_macos_install ${_version}
      _rv=$?
      ;;
    *)
      bes_message "Unsupported system: ${_system}"
      ;;
  esac
  return $_rv
}

function _bes_python_macos_install()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_python_install_macos version"
    return 1
  fi
  local _version=${1}
  local _url="https://www.python.org/ftp/python/${_version}/python-${_version}-macosx10.9.pkg"
  local _tmp=/tmp/_bes_python_macos_install_download_$$.pkg
  if ! bes_download ${_url} "${_tmp}"; then
    bes_message "_bes_python_macos_install: failed to download ${_url}"
    cat ${_tmp}
    rm -f ${_tmp}
    return 1
  fi
  local _rv=$?
  echo rv ${_rv}
  echo ${_tmp}
  return 0
}

# Return 0 if the given python executable is the sytem python that comes with macos
function _bes_python_macos_is_builtin()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_python_macos_is_builtin exe"
    return 1
  fi
  local _system=$(bes_system)
  if [[ ${_system} != "macos" ]]; then
    bes_message "_bes_python_macos_is_builtin: this only works on macos"
    return 1
  fi
  local _exe="${1}"
  if ! bes_path_is_abs "${_exe}"; then
    bes_message "_bes_python_macos_is_builtin: exe needs to be an absolute path"
    return 1
  fi
  if bes_str_starts_with "${_exe}" /usr/bin/python; then
    return 0
  fi
  return 1
}

# Return 0 if the given python executable is from brew
function _bes_python_macos_is_from_brew()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_python_macos_is_from_brew exe"
    return 1
  fi
  local _system=$(bes_system)
  if [[ ${_system} != "macos" ]]; then
    bes_message "_bes_python_macos_is_from_brew: this only works on macos"
    return 1
  fi
  local _exe="${1}"
  if ! bes_path_is_abs "${_exe}"; then
    bes_message "_bes_python_macos_is_from_brew: exe needs to be an absolute path"
    return 1
  fi
  local _real_exe
  if bes_path_is_symlink "${_exe}"; then
    _real_exe="$(readlink "${_exe}")"
  else
    _real_exe="${_exe}"
  fi
  if echo "${_real_exe}" | grep -i "cellar" >& /dev/null; then
    return 0
  fi
  return 1
}

# Return 0 if this macos has brew
function _bes_macos_has_brew()
{
  local _system=$(bes_system)
  if [[ ${_system} != "macos" ]]; then
    bes_message "_bes_macos_has_brew: this only works on macos"
    return 1
  fi
  if bes_has_program brew; then
    return 0
  fi
  return 1
}

# Print the "user-base" directory for a python executable
# on macos: ~/Library/Python/$major.$minor
# on linux: ~/.local
# Can also be controlled with PYTHONUSERBASE
function bes_python_user_base_dir()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_user_base_dir exe"
    return 1
  fi
  local _exe="${1}"
  if ! bes_path_is_abs "${_exe}"; then
    bes_message "bes_python_user_base_dir: exe needs to be an absolute path"
    return 1
  fi
  if [[ ! -x "${_exe}" ]] ;then
    echo ""
    return 1
  fi
  local _user_base_dir="$(PYTHONPATH= PATH= ${_exe} -m site --user-base)"
  echo "${_user_base_dir}"
  return 0
}

# Print the "user-site" directory for a python executable
# on macos: ~/Library/Python/$major.$minor/lib/python/site-packages
# on linux: ~/.local/lib/python$major.$minor/site-packages
function bes_python_user_site_dir()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_user_site_dir exe"
    return 1
  fi
  local _exe="${1}"
  if ! bes_path_is_abs "${_exe}"; then
    bes_message "bes_python_user_site: exe needs to be an absolute path"
    return 1
  fi
  if [[ ! -x "${_exe}" ]] ;then
    echo ""
    return 1
  fi
  local _user_site_dir="$(PYTHONPATH= PATH= ${_exe} -m site --user-site)"
  echo "${_user_site_dir}"
  return 0
}

# Print just the tail of "user-site" directory for a python executable
# usually:
#  lib/python/site-packages
#  lib/python$major.$minor/site-packages
function bes_python_user_site_dir_tail()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_user_site_dir_tail python_exe"
    return 1
  fi
  local _python_exe="${1}"

  bes_python_check_python_exe "${_python_exe}"

  local _fake_prefix=/tmp/notthere/
  local _user_site_dir="$(PYTHONUSERBASE=/tmp/notthere bes_python_user_site_dir "${_python_exe}")"
  local _user_site_dir_tail="$(bes_str_remove_head "${_user_site_dir}" ${_fake_prefix})"
  echo "${_user_site_dir_tail}"
  return 0
}

# Print the "user-base" bin directory for a python executable
# on macos: ~/Library/Python/$major.$minor/bin
# on linux: ~/.local/bin
# Can also be controlled with PYTHONUSERBASE
function bes_python_user_base_bin_dir()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_user_base_bin_dir exe"
    return 1
  fi
  local _exe="${1}"
  local _user_base_dir="$(bes_python_user_base_dir "${_exe}")"
  local _user_base_bin_dir="${_user_base_dir}/bin"
  echo "${_user_base_bin_dir}"
  return 0
}

# Print the "bin" dir for for a python executable
function bes_python_bin_dir()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_bin_dir exe"
    return 1
  fi
  local _exe="${1}"
  if ! bes_path_is_abs "${_exe}"; then
    bes_message "bes_python_bin_dir: exe needs to be an absolute path"
    return 1
  fi
  local _bin_dir="$(dirname ${_exe})"
  echo "${_bin_dir}"
  return 0
}

# Find a builtin python usually in /usr
function bes_python_find_builtin_python()
{
  local _possible_python
  for _possible_python in python3.7 python3.8 python2.7; do
    local _exe=/usr/bin/${_possible_python}
    if [[ -x "${_exe}" ]]; then
      echo "${_exe}"
      return 0
    fi
  done
  return 1
}

function bes_python_check_python_exe()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_check_python_exe python_exe"
    return 1
  fi
  local _label=${FUNCNAME[1]}
  local _python_exe="${1}"
  if ! bes_path_is_abs "${_python_exe}"; then
    bes_message "${_label}: not an absolute path: ${_python_exe}"
    exit 1
  fi
  if [[ ! -e "${_python_exe}" ]]; then
    bes_message "${_label}: not found: ${_python_exe}"
    exit 1
  fi
  if ! [[ -x "${_python_exe}" ]]; then
    bes_message "${_label}: not executable: ${_python_exe}"
    exit 1
  fi
  return 0
}

_bes_trace_file "end"
