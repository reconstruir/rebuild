#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to deal with pip

_bes_trace_file "begin"

# Call program from the pip userbase
function bes_pip_call_program()
{
  if [[ $# < 3 ]]; then
    bes_message "Usage: bes_pip_call_program python_exe user_base_dir program"
    return 1
  fi
  
  local _python_exe="${1}"
  shift
  bes_python_check_python_exe "${_python_exe}"

  local _user_base_dir="${1}"
  shift

  local _program="${1}"
  shift
  
  local _user_base_bin_dir="$(bes_abs_dir "${_user_base_dir}/bin")"
  local _program_abs="$(bes_abs_file "${_user_base_bin_dir}/${_program}")"

  local _user_site_dir_tail="$(bes_python_user_site_dir_tail "${_python_exe}")"
  local _user_site_dir="${_user_base_dir}/${_user_site_dir_tail}"
  PYTHONUSERBASE="${_user_base_dir}" PATH="${_user_base_bin_dir}":"${PATH}" PYTHONPATH="${_user_site_dir}":"${PYTHONPATH}" "${_python_exe}" -S "${_program_abs}" ${1+"$@"}
  local _program_rv=$?
  return ${_program_rv}
}

# Call pip
function bes_pip_call()
{
  if [[ $# < 2 ]]; then
    bes_message "Usage: bes_pip_call python_exe user_base_dir"
    return 1
  fi
  local _python_exe="${1}"
  shift
  bes_python_check_python_exe "${_python_exe}"

  local _user_base_dir="${1}"
  shift

  local _python_version=$(bes_python_exe_version "${_python_exe}")
  local _pip_basename=pip${_python_version}

  local _extra_args=
  if [[ -n "${BES_PIP_EXTRA_ARGS}" ]]; then
    _extra_args="${BES_PIP_EXTRA_ARGS}"
  fi
  
  bes_pip_call_program "${_python_exe}" "${_user_base_dir}" ${_pip_basename} ${_extra_args} ${1+"$@"}
  local _pip_rv=$?
  return ${_pip_rv}
}

# Print the full version of pip
function bes_pip_exe_version()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: bes_pip_exe_version python_exe pip_exe"
    return 1
  fi
  local _python_exe="${1}"
  local _pip_exe="${2}"

  local _pip_dir="$(dirname "${_pip_exe}")"
  local _user_base_dir="$(bes_abs_dir "${_pip_dir}"/..)"

  local _full_version=$(bes_pip_call "${_python_exe}" "${_user_base_dir}" --version | ${_BES_AWK_EXE} '{ print $2; }')
  echo "${_full_version}"
  return 0
}

# Print the absolute path to the user pip exe that corresponds to the given python exe
function bes_pip_exe()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: bes_pip_exe python_exe user_base_dir"
    return 1
  fi
  local _python_exe="${1}"
  if ! bes_path_is_abs "${_python_exe}"; then
    bes_message "bes_pip_exe: python_exe needs to be an absolute path"
    return 1
  fi
  local _user_base_dir="${2}"
  local _python_version=$(bes_python_exe_version "${_python_exe}")
  local _pip_basename=pip${_python_version}
  local _user_base_pip_abs="${_user_base_dir}/bin/${_pip_basename}"
  echo ${_user_base_pip_abs}
  return 1
}

# Return 0 if there is a user pip
function bes_pip_has_pip()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: bes_pip_has_pip python_exe user_base_dir"
    return 1
  fi
  local _python_exe="${1}"
  if ! bes_path_is_abs "${_python_exe}"; then
    bes_message "bes_pip_has_pip: python_exe needs to be an absolute path"
    return 1
  fi
  local _user_base_dir="${2}"
  local _pip_exe="$(bes_pip_exe "${_python_exe}" "${_user_base_dir}")"
  if [[ -x "${_pip_exe}" ]]; then
    return 0
  fi
  return 1
}

# Install pip for the first time
function bes_pip_install()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_pip_install python_exe user_base_dir"
    return 1
  fi
  local _python_exe="${1}"
  if ! bes_path_is_abs "${_python_exe}"; then
    bes_message "bes_pip_install: python_exe needs to be an absolute path"
    return 1
  fi
  local _user_base_dir="${2}"
  
  if bes_pip_has_pip "${_python_exe}" "${_user_base_dir}"; then
    local _pip_exe="$(bes_pip_exe "${_python_exe}")"
    bes_message "pip already installed: ${_pip_exe}"
    return 1
  fi

  local _GET_PIP_URL="https://bootstrap.pypa.io/get-pip.py"
  local _tmp_get_pip_dot_py=/tmp/tmp_bes_pip_install_get_pip_$$.py
  rm -f "${_tmp_get_pip_dot_py}"
  if ! bes_download "${_GET_PIP_URL}" "${_tmp_get_pip_dot_py}"; then
    rm -f "${_tmp_get_pip_dot_py}"
    bes_message "Failed to download ${_GET_PIP_URL} to ${_tmp_get_pip_dot_py}"
    return 1
  fi
  local _extra_args=
  if [[ -n "${BES_PIP_EXTRA_ARGS}" ]]; then
    _extra_args="${BES_PIP_EXTRA_ARGS}"
  fi
  local _tmp_log=/tmp/tmp_bes_pip_install_$$.log
  if ! PYTHONUSERBASE="${_user_base_dir}" "${_python_exe}" ${_tmp_get_pip_dot_py} ${_extra_args} --user >& "${_tmp_log}"; then
    bes_message "Failed to install pip in ${_user_base_dir} with ${_python_exe}"
    cat "${_tmp_log}"
    rm -f "${_tmp_get_pip_dot_py}" "${_tmp_log}"
    return 1
  fi
  rm -f "${_tmp_get_pip_dot_py}" "${_tmp_log}"

  if ! bes_pip_has_pip "${_python_exe}" "${_user_base_dir}"; then
    bes_message "pip install succeeded but failing to find pip afterwards"
    return 1
  fi

  local _pip_exe="$(bes_pip_exe "${_python_exe}" "${_user_base_dir}")"
  
  if [[ ! -x "${_pip_exe}" ]]; then
    bes_message "pip install succeeded but failing execute: ${_pip_exe}"
    return 1
  fi
  return 0
}

# Update pip to specific version
function bes_pip_update()
{
  if [[ $# != 3 ]]; then
    echo "usage: bes_pip_update python_exe user_base_dir pip_version"
    return 1
  fi
  local _python_exe="${1}"
  local _user_base_dir="${2}"
  local _pip_version=${3}

  if ! bes_pip_has_pip "${_python_exe}" "${_user_base_dir}"; then
    bes_message "bes_pip_update: pip is not installed in ${_user_base_dir}"
    return 1
  fi

  local _pip_exe="$(bes_pip_exe "${_python_exe}" "${_user_base_dir}")"
  local _current_pip_version=$(bes_pip_exe_version "${_python_exe}" "${_pip_exe}")
  
  if [[ ${_current_pip_version} == ${_pip_version} ]]; then
    return 0
  fi

  #FIXME: make a backup in case the upgrade fails out and leaves things inconsistent
  local _tmp_log=/tmp/tmp_bes_pip_update_$$.log
  if ! bes_pip_call "${_python_exe}" "${_user_base_dir}" install --user pip==${_pip_version} >& "${_tmp_log}"; then
    bes_message "1 Failed to update pip from ${_current_pip_version} to ${_pip_version}"
    cat "${_tmp_log}"
    rm -f "${_tmp_log}"
    return 1
  fi
  rm -f "${_tmp_log}"
    
  local _new_current_pip_version=$(bes_pip_exe_version "${_python_exe}" "${_pip_exe}")
  if [[ ${_new_current_pip_version} != ${_pip_version} ]]; then
    bes_message "2 Failed to update pip from ${_current_pip_version} to ${_pip_version}"
    return 1
  fi
  
  return 0
}

# Ensure that user pip is installed and at the given version
function bes_pip_ensure()
{
  if [[ $# != 3 ]]; then
    echo "usage: bes_pip_ensure python_exe user_base_dir pip_version"
    return 1
  fi
  local _python_exe="${1}"
  if ! bes_path_is_abs "${_python_exe}"; then
    bes_message "bes_pip_ensure: python_exe needs to be an absolute path"
    return 1
  fi
  local _user_base_dir="${2}"
  local _pip_version="${3}"

  if ! bes_pip_has_pip "${_python_exe}" "${_user_base_dir}"; then
    if ! bes_pip_install "${_python_exe}" "${_user_base_dir}"; then
      return 1
    fi
  fi

  bes_pip_update "${_python_exe}" "${_user_base_dir}" ${_pip_version}
  local _rv=$?
  return ${_rv}
}

# Use pip to install a package
function bes_pip_install_package()
{
  if [[ $# < 3 ]]; then
    echo "usage: bes_pip_install_package python_exe pip_exe package_name <package_version>"
    return 1
  fi
  local _python_exe="${1}"
  shift
  if [[ ! -x "${_python_exe}" ]]; then
    bes_message "bes_pip_install_package: cannot execute python: ${_python_exe}"
    return 1
  fi
  
  local _pip_exe="${1}"
  shift
  
  if [[ ! -x "${_pip_exe}" ]]; then
    bes_message "bes_pip_install_package: cannot execute pip: ${_pip_exe}"
    return 1
  fi
  
  local _package_name=${1}
  shift
  
  local _package_version=
  local _install_arg=
  if [[ $# > 0 ]]; then
    _package_version=${1}
    _install_arg=${_package_name}==${_package_version}
  else
    _package_version=
    _install_arg=${_package_name}
  fi

  local _tmp_log=/tmp/tmp_bes_pip_install_package_$$.log
  rm -f "${_tmp_log}"

  local _pip_dir="$(dirname "${_pip_exe}")"
  local _user_base_dir="$(bes_abs_dir "${_pip_dir}"/..)"

  if ! bes_pip_call "${_python_exe}" "${_user_base_dir}" install --user ${_install_arg} >& "${_tmp_log}"; then
    bes_message "Failed to install ${_install_arg} with ${_pip_exe}"
    cat "${_tmp_log}"
    rm -f "${_tmp_log}"
    return 1
  fi
  rm -f "${_tmp_log}"
  return 0
}

_bes_trace_file "end"
