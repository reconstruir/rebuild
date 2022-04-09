#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

function _bes_bash_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

_BES_BASH_THIS_DIR="$(_bes_bash_this_dir)"

function _bes_trace() ( if [[ "$_BES_TRACE" == "1" ]]; then printf '_BES_TRACE: %s\n' "$*"; fi )
function _bes_trace_function() ( _bes_trace "func: ${FUNCNAME[1]}($*)" )
function _bes_trace_file() ( _bes_trace "file: ${BASH_SOURCE}: $*" )

function bes_import()
{
  _bes_trace_function $*

  if [[ $# != 1 ]]; then
    echo "usage: bes_import filename"
    return 1
  fi

  local _filename="${1}"
  local _this_dir="$(_bes_bash_this_dir)"
  local _filename_abs="${_this_dir}/${_filename}"

  if _bes_import_filename_is_imported "${_filename_abs}"; then
    return 0
  fi
  
  if [[ ! -f "${_filename_abs}" ]]; then
    local _basename="$(basename ${_filename_abs})"
    echo "bes_import: ${BASH_SOURCE[1]}:${BASH_LINENO[0]}: file \"${_basename}\" not found in ${_this_dir}"
    exit 1
  fi

  source "${_filename_abs}"
  _bes_import_filename_set_imported "${_filename_abs}"
  return 0
}

function _bes_import_filename_variable_name()
{
  if [[ $# != 1 ]]; then
    echo "usage: _bes_import_filename_variable_name filename"
    return 1
  fi

  local _filename="${1}"
  local _basename="$(basename "${_filename}")"
  local _sanitized_basename=$(echo ${_basename} | tr '[:punct:]' '_' | tr '[:space:]' '_')
  local _var_name=__imported_${_sanitized_basename}__
  echo ${_var_name}
  return 0
}

function _bes_import_filename_set_imported()
{
  if [[ $# != 1 ]]; then
    echo "usage: _bes_import_filename_mark_imported filename"
    return 1
  fi
  local _filename="${1}"
  local _var_name=$(_bes_import_filename_variable_name "${_filename}")
  eval "${_var_name}=\"true\""
  return 0
}

function _bes_import_filename_is_imported()
{
  if [[ $# != 1 ]]; then
    echo "usage: _bes_import_filename_is_imported filename"
    return 1
  fi
  local _filename="${1}"
  local _var_name=$(_bes_import_filename_variable_name "${_filename}")
  local _var_value=$(eval 'printf "%s\n" "${'"${_var_name}"'}"')
  if [[ "${_var_value}" == "true" ]]; then
    return 0
  fi
  return 1
}

# Source a shell file or print an error if it does not exist
function bes_source_file()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    echo "Usage: bes_source_file filename"
    return 1
  fi
  local _filename="${1}"
  if [[ ! -e "${_filename}" ]]; then
    echo "bes_source_file: File not found: ${_filename}"
    return 1
  fi
  if [[ ! -f "${_filename}" ]]; then
    echo "bes_source_file: Not a file: ${_filename}"
    return 1
  fi
  source "${_filename}"
  return 0
}

# Source a shell file but only if it exists
function bes_source_file_if()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_source filename\n\n"
    return 1
  fi
  local _filename="${1}"
  if [[ ! -f "${_filename}" ]]; then
    return 1
  fi
  bes_source_file "${_filename}"
  return $?
}

# Return an exit code of 0 if the argument is "true."  true is one of: true, 1, t, yes, y
function bes_is_true()
{
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_is_true what\n\n"
    return 1
  fi
  local _what=$( echo "$1" | $_BES_TR_EXE '[:upper:]' '[:lower:]' )
  local _rv
  case "${_what}" in
    true|1|t|y|yes)
      _rv=0
      ;;
    *)
      _rv=1
      ;;
  esac
  return ${_rv}
}

function bes_script_name()
{
  if [[ -n "${_BES_SCRIPT_NAME}"  ]]; then
    echo "${_BES_SCRIPT_NAME}"
    return 0
  fi
  if [[ ${0} =~ .+bash$ ]]; then
    echo "bes_bash"
    return 0
  fi
  echo $(basename "${0}")
  return 0
}

function bes_message()
{
  local _script_name=$(bes_script_name)
  echo ${_script_name}: ${1+"$@"}
  return 0
}

function bes_debug_message()
{
  if [[ -z "${BES_DEBUG}" ]]; then
    return 0
  fi
  local _output=""
  if [[ -n "${BES_LOG_FILE}" ]]; then
    _output="${BES_LOG_FILE}"
  else
    if [[ -t 1 ]]; then
      _output=$(tty)
    fi
  fi
  local _script_name=$(bes_script_name)
  local _pid=$$
  local _message=$(printf "%s(%s): %s\n" ${_script_name} ${_pid} ${1+"$@"})
  if [[ -n "${_output}" ]]; then
    echo ${_message} >> ${_output}
  else
    echo ${_message}
  fi
  return 0
}

function bes_console_message()
{
  if bes_is_ci ; then
    BES_DEBUG=1 bes_debug_message ${1+"$@"}
  else    
    BES_DEBUG=1 BES_LOG_FILE=$(tty) bes_debug_message ${1+"$@"}
  fi
  return $?
}

function bes_function_exists()
{
  local _name=${1}
  local _type=$(type -t ${_name})
  if [[ "${_type}" == "function" ]]; then
    return 0
  else
    return 1
  fi
}

function _bes_function_invoke()
{
  _bes_trace_function $*
  if [[ $# < 2 ]]; then
    printf "\nUsage: _bes_function_invoke function default_rv args\n\n"
    return 1
  fi
  local _function=${1}
  shift
  local _default_rv=${1}
  shift
  local _rv=${_default_rv}
  if bes_function_exists ${_function}; then
    eval ${_function} ${1+"$@"}
    _rv=$?
  fi
  return ${_rv}
}

# invoke a function if it exists.  returns exit code of function or 1 if the function does not exist.
function bes_function_invoke()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_function_invoke_if function args\n\n"
    return 1
  fi
  local _function=${1}
  shift
  _bes_function_invoke ${_function} 1 ${1+"$@"}
  local _rv=$?
  return ${_rv}
}

# invoke a function if it exists.  returns exit code of function or 0 if the function does not exist.
function bes_function_invoke_if()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_function_invoke_if function args\n\n"
    return 1
  fi
  local _function=${1}
  shift
  _bes_function_invoke ${_function} 0 ${1+"$@"}
  local _rv=$?
  return ${_rv}
}

# atexit function suitable for trapping and printing the exit code
# trap "bes_atexit_message_successful ${_remote_name}" EXIT
function bes_atexit_message_successful()
{
  local _actual_exit_code=$?
  if [[ ${_actual_exit_code} == 0 ]]; then
    bes_message success ${1+"$@"}
  else
    bes_message failed ${1+"$@"}
  fi
  return ${_actual_exit_code}
}

function bes_atexit_remove_dir_handler()
{
  local _actual_exit_code=$?
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_atexit_remove_dir_handler dir"
    return 1
  fi
  local _dir="${1}"
  if [[ -e "${_dir}" ]]; then
    if [[ ! -d "${_dir}" ]]; then
      bes_message "_bes_atexit_remove_dir_handler: not a directory: ${_dir}"
      return 1
    fi
    bes_debug_message "_bes_atexit_remove_dir_handler: removing ${_dir}"
    /bin/rm -rf ${_dir}
  else
    bes_debug_message "_bes_atexit_remove_dir_handler: directory not found ${_dir}"
  fi
  return ${_actual_exit_code}
}

# Get a var value
function bes_var_get()
{
  eval 'printf "%s\n" "${'"$1"'}"'
}

# Set a var value
function bes_var_set()
{
  eval "$1=\"\$2\""
}

# Unset a var value
function bes_var_unset()
{
  eval "unset $1"
}

# Export a var value
function bes_var_export()
{
  eval "export $1=\"\$2\""
}

_BES_LOG_FILE=$(tty)

function bes_log()
{
  if [[ $# < 3 ]]; then
    echo "Usage: bes_log component level <message>"
    return 1
  fi
  local _component=${1}
  shift
  local _level=${1}
  shift
  if ! bes_log_level_matches ${_component} ${_level}; then
    return 0
  fi
  local _timestamp=$(date +"%Y_%m_%d-%H:%M:%S-%Z")
  local _pid="$$"
  local _label="${_component}.${_level}"
  local _text=$(printf "${_timestamp} [${_pid}] (${_label}) %s\n" "$*")
  if [[ -z "${_BES_LOG_FILE}" ]]; then
    echo "${_text}"
  else
    echo "${_text}" > ${_BES_LOG_FILE}
  fi
  return 0
}

function bes_log_level_set()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_log_level_set component error|warning|info|debug|trace"
    return 1
  fi
  local _component=${1}
  local _level=${2}
  _bes_log_level_check bes_log_level_set ${_level}
  local _var_name="_BES_LOG_CONFIG_${_component}"
  bes_var_set ${_var_name} ${_level}
}

function bes_log_level_get()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_log_level_get component"
    return 1
  fi
  local _component=${1}
  local _var_name="_BES_LOG_CONFIG_${_component}"
  local _level="$(bes_var_get ${_var_name})"
  if [[ -z "${_level}" ]]; then
    _level=error
  fi
  echo ${_level}
  return 0
}

function bes_log_level_matches()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_log_level_matches component error|warning|info|debug|trace"
    return 1
  fi
  local _component=${1}
  local _level=${2}
  _bes_log_level_check bes_log_level_matches ${_level}
  local _current_level=$(bes_log_level_get ${_component})
  case "${_current_level}" in
    error)
      case "${_level}" in
        error)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    warning)
      case "${_level}" in
        error|warning)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    info)
      case "${_level}" in
        error|warning|info)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    debug)
      case "${_level}" in
        error|warning|info|debug)
          return 0
          ;;
        *)
          return 1
          ;;
      esac
      ;;
    trace)
      return 0
      ;;
  esac
  return 1
}

function bes_log_config()
{
  local _items=(${@})
  local _item
  for _item in "${_items[@]}"; do
    local _component=$(echo ${_item} | awk -F"=" '{ print $1; }')
    local _level=$(echo ${_item} | awk -F"=" '{ print $2; }')
    if [[ -z "${_level}" ]]; then
      _level=error
    fi
    bes_log_level_set ${_component} ${_level}
  done
}

function _bes_log_level_is_valid()
{
  if [[ $# != 1 ]]; then
    echo "Usage: _bes_log_level_is_valid level"
    return 1
  fi
  local _level=${1}
  case "${_level}" in
    error|warning|info|debug|trace)
      return 0
      ;;
    *)
      ;;
  esac
  return 1
}

function _bes_log_level_check()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_log_level_is_valid label level"
    return 1
  fi
  local _label=${1}
  local _level=${2}
  if ! _bes_log_level_is_valid ${_level}; then
    echo "$_label: Invalid log level: ${_level}.  Should be one of error|warning|info|debug|trace"
    exit 1
  fi
  return 0
}

if [[ -n ${BES_LOG} ]]; then
  bes_log_config "${BES_LOG}"
fi

function bes_log_trace_function()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_log_trace_function component"
    return 1
  fi
  local _component=${1}
  shift
  bes_log ${_component} trace "${FUNCNAME[1]}($*)"
}

function bes_log_trace_file()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_log_trace_function component"
    return 1
  fi
  local _component=${1}
  shift
  bes_log ${_component} trace "${BASH_SOURCE}: ($*)"
}

function bes_log_set_log_file()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_log_set_log_file log_file"
    return 1
  fi
  local _log_file="${1}"
  _BES_LOG_FILE="${_log_file}"
  return 0
}
_bes_import_filename_set_imported "bes_bfg.bash"
_bes_import_filename_set_imported "bes_brew.bash"
_bes_import_filename_set_imported "bes_checksum.bash"
_bes_import_filename_set_imported "bes_cicd.bash"
_bes_import_filename_set_imported "bes_dev.bash"
_bes_import_filename_set_imported "bes_dominictarr_json.bash"
_bes_import_filename_set_imported "bes_download.bash"
_bes_import_filename_set_imported "bes_file.bash"
_bes_import_filename_set_imported "bes_filename.bash"
_bes_import_filename_set_imported "bes_git.bash"
_bes_import_filename_set_imported "bes_git_subtree.bash"
_bes_import_filename_set_imported "bes_json.bash"
_bes_import_filename_set_imported "bes_list.bash"
_bes_import_filename_set_imported "bes_path.bash"
_bes_import_filename_set_imported "bes_pip_project.bash"
_bes_import_filename_set_imported "bes_python.bash"
_bes_import_filename_set_imported "bes_question.bash"
_bes_import_filename_set_imported "bes_string.bash"
_bes_import_filename_set_imported "bes_system.bash"
_bes_import_filename_set_imported "bes_testing.bash"
_bes_import_filename_set_imported "bes_version.bash"
_bes_import_filename_set_imported "bes_web.bash"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to call bfg

_bes_trace_file "begin"

function bes_bfg_call()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: version"
    return 1
  fi
  if ! $(bes_has_program java); then
    bes_message "java not f.ound"
    return 1
  fi
  local _version="${1}"
  shift
  local _local_jar="${HOME}/.besbfg/bfg/bfg-${_version}.jar"
  _bfg_download ${_version} "${_local_jar}"
  bes_message "calling: java -jar ${_local_jar} "${1+"$@"}
  java -jar ${_local_jar} ${1+"$@"}
  local _rv=$?
  return ${_rv}
}

function _bfg_download()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: _bfg_download version local_jar"
    return 1
  fi
  local _version="${1}"
  local _local_jar="${2}"
  local _version="${1}"
  shift
  
  if [[ ! -f ${_local_jar} ]]; then
    local _url="https://repo1.maven.org/maven2/com/madgag/bfg/${_version}/bfg-${_version}.jar"
    bes_download "${_url}" "${_local_jar}"
  fi
  if [[ ! -f ${_local_jar} ]]; then
    bes_message "failed to download: ${_url} to ${_local_jar}"
    return 1
  fi

  local _actual_version=$(bfg_version ${_local_jar})
  if [[ ${_actual_version} != ${_version} ]]; then
    bes_message "version mismatch error.  should be ${_version} instead of ${_actual_version}"
    return 1
  fi
  
  return 0
}

function bfg_version()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bfg_jar"
    return 1
  fi
  local _bfg_jar="${1}"
  local _version=$(java -jar ${_bfg_jar} --version | awk '{ print $2; }')
  echo ${_version}
  return 0
}

_bes_trace_file "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to deal with brew on macos

_bes_trace_file "begin"

# Return 0 if this macos has brew
function bes_has_brew()
{
  local _system=$(bes_system)
  if [[ ${_system} != "macos" ]]; then
    bes_message "bes_has_brew: this only works on macos"
    return 1
  fi
  if bes_has_program brew; then
    return 0
  fi
  return 1
}

# Install brew
function bes_brew_install()
{
  local _system=$(bes_system)
  if [[ ${_system} != "macos" ]]; then
    bes_message "bes_brew_install: this only works on macos"
    return 1
  fi
  if bes_has_brew; then
    return 0
  fi
  return 1
}

_bes_trace_file "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file checksum "begin"

# Checksum file using algorithm
function bes_checksum_file()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_checksum_file algorithm filename"
    return 1
  fi
  local _algorithm="${1}"
  local _filename="${2}"
  local _system=$(bes_system)
  local _result
  local _rv
  case "${_system}" in
    linux|windows)
      _result=$(_bes_checksum_file_linux ${_algorithm}  "${_filename}")
      _rv=$?
      ;;
    macos)
      _result=$(_bes_checksum_file_macos ${_algorithm}  "${_filename}")
      _rv=$?
      ;;
    *)
      echo "unknown system: ${_system}"
      return 1
      ;;
  esac
  echo ${_result}
  return ${_rv}
}

# Checksum text using algorithm
function bes_checksum_text()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_checksum_text algorithm text"
    return 1
  fi
  local _algorithm="${1}"
  local _text="${2}"
  local _system=$(bes_system)
  local _result
  local _rv
  case "${_system}" in
    linux|windows)
      _result=$(_bes_checksum_text_linux ${_algorithm}  "${_text}")
      _rv=$?
      ;;
    macos)
      _result=$(_bes_checksum_text_macos ${_algorithm}  "${_text}")
      _rv=$?
      ;;
    *)
      echo "unknown system: ${_system}"
      return 1
      ;;
  esac
  echo ${_result}
  return ${_rv}
}

# Checksum only the files in a directory.  Empty directories are ignored.
function bes_checksum_dir_files()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_checksum_dir_files algorithm dir"
    return 1
  fi
  local _algorithm="${1}"
  local _dir="${2}"
  local _file
  local _checksum
  local _checksums=$(cd ${_dir} && find . -type f -print0 | while read -d $'\0' _file; do
    _checksum=$(bes_checksum_file ${_algorithm} "${_file}")
    printf "%s %s\n" "${_file}" "${_checksum}" | $_BES_TR_EXE ' ' '_'
  done | sort)
  local _result=$(bes_checksum_text ${_algorithm} "${_checksums}")
  echo ${_result}
  return 0
}

# Checksum a manifest of files
function bes_checksum_manifest()
{
  if [[ $# != 3 ]]; then
    echo "Usage: bes_checksum_manifest algorithm dir manifest"
    return 1
  fi
  local _algorithm="${1}"
  local _dir="${2}"
  local _manifest="${3}"
  if [[ ! -f "${_manifest}" ]]; then
    echo "bes_checksum_manifest: manifest not found: ${_manifest}"
    return 1
  fi
  local _file
  local _checksum
  local _saveIFS="${IFS}"
  IFS=''
  local _checksums=$(while read _file; do
    _checksum=$(bes_checksum_file ${_algorithm} "${_dir}/${_file}")
    printf "%s %s\n" "${_file}" "${_checksum}" | $_BES_TR_EXE ' ' '_'
  done < "${_manifest}" | sort)
  IFS="${_saveIFS}"
  local _result=$(bes_checksum_text ${_algorithm} "${_checksums}")
  echo ${_result}
  return 0
}

function _bes_checksum_text_macos()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_text_macos algorithm text"
    return 1
  fi
  local _algorithm="${1}"
  local _text="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(echo "${_text}" | md5)
      ;;
    sha1)
      _result=$(echo "${_text}" | shasum -a 1 | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(echo "${_text}" | shasum -a 256 | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(echo "${_text}" | shasum -a 512 | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

function _bes_checksum_file_macos()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_file_macos algorithm filename"
    return 1
  fi
  local _algorithm="${1}"
  local _filename="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(md5 -q "${_filename}")
      ;;
    sha1)
      _result=$(shasum -a 1 "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(shasum -a 256 "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(shasum -a 512 "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

function _bes_checksum_file_linux()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_file_linux algorithm filename"
    return 1
  fi
  local _algorithm="${1}"
  local _filename="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(md5sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha1)
      _result=$(sha1sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(sha256sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(sha512sum "${_filename}" | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

function _bes_checksum_text_linux()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_checksum_text_linux algorithm text"
    return 1
  fi
  local _algorithm="${1}"
  local _text="${2}"
  local _result
  case "${_algorithm}" in
    md5)
      _result=$(echo "${_text}" | md5sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha1)
      _result=$(echo "${_text}" | sha1sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha256)
      _result=$(echo "${_text}" | sha256sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    sha512)
      _result=$(echo "${_text}" | sha512sum | ${_BES_AWK_EXE} '{ print($1); }')
      ;;
    *)
      echo "unknown algorithm: ${_algorithm}"
      return 1
      ;;
  esac
  echo ${_result}
  return 0
}

function bes_checksum_check_file()
{
  # Return True (0) if filename matches the checksum written in checksum_filename"
  if [[ $# != 2 ]]; then
    echo "Usage: bes_checksum_check_file filename checksum_filename"
    return 1
  fi
  local _filename="${1}"
  local _checksum_filename="${2}"
  if [[ ! -f "${_checksum_filename}" ]]; then
    return 1
  fi
  local _old_checksum=$(cat "${_checksum_filename}")
  local _new_checksum=$(bes_checksum_file "sha256" "${_filename}")
  if [[ ${_old_checksum} == ${_new_checksum} ]]; then
    return 0
  fi
  return 1
}

bes_log_trace_file checksum "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Return 0 if currently running under a CICD system
function bes_cicd_running_under_cicd()
{
  # bitbucket,github
  if [[ -n "${CI}" ]]; then
    return 0
  fi
  # jenkins
  if [[ -n "${HUDSON_COOKIE}" ]]; then
    return 0
  fi
  # gitlab
  if [[ -n "${GITLAB_CI}" ]]; then
    return 0
  fi
  return 1
}
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file path "begin"

function bes_dev_set_tab_title()
{
  echo -ne "\033]0;"$*"\007"
  local _prompt=$(echo -ne "\033]0;"$*"\007")
  export PROMPT_COMMAND='${_prompt}'
}

function bes_dev_unsetup()
{
  _bes_trace_function $*
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_dev_unsetup root_dir\n\n"
    return 1
  fi
  local _root_dir="${1}"
  bes_env_path_remove PATH "${_root_dir}/bin"
  bes_env_path_remove PYTHONPATH "${_root_dir}/lib"
  bes_dev_set_tab_title ""
  return 0
}

function bes_dev_setup()
{
  function _bes_dev_setup_help()
  {
    cat << EOF
Usage: bes_dev_setup <options> root_dir

  Where options is one or more of:

    -h,--help                  Show this help.
    --set-title                Set the title terminal [ true ]
    --no-set-title,-nst        Dont set the title [ false ]
    --change-dir               Change dir [ true ]
    --no-change-dir,-ncd       Dont change dir [ false ]
    --set-python-path
    --set-path
    --no-venv-activate,-nva
    --venv-config
    --venv-activate
    --light,-l                 Same as giving all these flags:
                                 -set-path
                                 -set-python-path
                                 -no-set-title
                                 -no-venv-activate
                                 -no-change-dir
EOF
  }

  _bes_trace_function $*

  local _set_title=false
  local _change_dir=false
  local _set_path=false
  local _set_pythonpath=false
  local _venv_config=
  local _positional_args=()
  local _key
  while [[ $# -gt 0 ]]; do
    _key="${1}"
    bes_debug_message "bes_dev_setup: checking key ${_key} ${2}"
    case ${_key} in
      --venv-config)
        _venv_config="${2}"
        shift # past argument
        shift # past value
        ;;
      --venv-activate)
        _venv_activate=true
        shift # past argument
        ;;
      --no-venv-activate|-nva)
        _venv_activate=false
        shift # past argument
        ;;
      --set-path)
        _set_path=true
        shift # past argument
        ;;
      --no-set-path)
        _set_path=false
        shift # past argument
        ;;
      --set-python-path)
        _set_pythonpath=true
        shift # past argument
        ;;
      --no-set-python-path)
        _set_pythonpath=false
        shift # past argument
        ;;
      --change-dir)
        _change_dir=true
        shift # past argument
        ;;
      --no-change-dir)
        _change_dir=false
        shift # past argument
        ;;
      --set-title)
        _set_title=true
        shift # past argument
        ;;
      --no-set-title)
        _set_title=false
        shift # past argument
        ;;
      --light|-l)
        _set_path=true
        _set_pythonpath=true
        _set_title=false
        _venv_activate=false
        _change_dir=false
        shift # past argument
        ;;
      --help|-h)
        _bes_dev_setup_help
        shift # past argument
        return 0
        ;;
      *)    # unknown option
        _positional_args+=("${1}") # save it in an array for later
        shift # past argument
        ;;
    esac
  done
  
  set -- "${_positional_args[@]}" # restore positional parameters

  local _root_dir=
  if [[ $# < 1 ]]; then
    _bes_dev_setup_help
    return 1
  fi
  if [[ $# > 0 ]]; then
    _root_dir="${1}"
    shift
  fi
  if [[ $# > 0 ]]; then
    printf "\nbes_dev_setup: unknown arguments: $*\n\n"
    return 1
  fi
  if [[ ${_set_path} == true ]]; then
    bes_env_path_prepend PATH "${_root_dir}/bin"
  fi
  if [[ ${_set_pythonpath} == true ]]; then
    bes_env_path_prepend PYTHONPATH "${_root_dir}/lib"
  fi
  if [[ ${_change_dir} == true ]]; then
    cd "${_root_dir}"
  fi
  if [[ ${_set_title} == true ]]; then
    bes_dev_set_tab_title $($_BES_BASENAME_EXE "${_root_dir}")
  fi
  if [[ -n "${_venv_config}" ]]; then
    if [[ ! -f "${_venv_config}" ]]; then
      printf "\nbes_dev_setup: venv activate config not found: ${_venv_config}\n\n"
      return 1
    fi
    if [[ ${_venv_activate} == true ]]; then
      source "${_venv_config}"
    fi
  fi
  return 0
}

bes_log_trace_file path "end"
#!/bin/sh

# turn this on for debugging with bes logging
#function _bes_dominictarr_json_this_dir()
#{
#  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#  return 0
#}
#source "$(_bes_dominictarr_json_this_dir)/bes_basic.bash"

#
# this code borrowed from here:
# https://github.com/dominictarr/JSON.sh
#
throw() {
  #bes_debug_message "$*"
  echo "$*" >&2
  exit 1
}

BRIEF=0
LEAFONLY=0
PRUNE=0
NO_HEAD=0
NORMALIZE_SOLIDUS=0

usage() {
  echo
  echo "Usage: bes_dominictarr_json.sh [-b] [-l] [-p] [-s] [-h]"
  echo
  echo "-p - Prune empty. Exclude fields with empty values."
  echo "-l - Leaf only. Only show leaf nodes, which stops data duplication."
  echo "-b - Brief. Combines 'Leaf only' and 'Prune empty' options."
  echo "-n - No-head. Do not show nodes that have no path (lines that start with [])."
  echo "-s - Remove escaping of the solidus symbol (straight slash)."
  echo "-h - This help text."
  echo
}

parse_options() {
  set -- "$@"
  local ARGN=$#
  while [ "$ARGN" -ne 0 ]
  do
    case $1 in
      -h) usage
          exit 0
      ;;
      -b) BRIEF=1
          LEAFONLY=1
          PRUNE=1
      ;;
      -l) LEAFONLY=1
      ;;
      -p) PRUNE=1
      ;;
      -n) NO_HEAD=1
      ;;
      -s) NORMALIZE_SOLIDUS=1
      ;;
      ?*) echo "ERROR: Unknown option."
          usage
          exit 0
      ;;
    esac
    shift 1
    ARGN=$((ARGN-1))
  done
}

awk_egrep () {
  local pattern_string=$1

  gawk '{
    while ($0) {
      start=match($0, pattern);
      token=substr($0, start, RLENGTH);
      print token;
      $0=substr($0, start+RLENGTH);
    }
  }' pattern="$pattern_string"
}

tokenize () {
  local GREP
  local ESCAPE
  local CHAR

  if echo "test string" | egrep -ao --color=never "test" >/dev/null 2>&1
  then
    GREP='egrep -ao --color=never'
  else
    GREP='egrep -ao'
  fi

  if echo "test string" | egrep -o "test" >/dev/null 2>&1
  then
    ESCAPE='(\\[^u[:cntrl:]]|\\u[0-9a-fA-F]{4})'
    CHAR='[^[:cntrl:]"\\]'
  else
    GREP=awk_egrep
    ESCAPE='(\\\\[^u[:cntrl:]]|\\u[0-9a-fA-F]{4})'
    CHAR='[^[:cntrl:]"\\\\]'
  fi

  local STRING="\"$CHAR*($ESCAPE$CHAR*)*\""
  local NUMBER='-?(0|[1-9][0-9]*)([.][0-9]*)?([eE][+-]?[0-9]*)?'
  local KEYWORD='null|false|true'
  local SPACE='[[:space:]]+'

  # Force zsh to expand $A into multiple words
  local is_wordsplit_disabled=$(unsetopt 2>/dev/null | grep -c '^shwordsplit$')
  if [ $is_wordsplit_disabled != 0 ]; then setopt shwordsplit; fi
  $GREP "$STRING|$NUMBER|$KEYWORD|$SPACE|." | egrep -v "^$SPACE$"
  if [ $is_wordsplit_disabled != 0 ]; then unsetopt shwordsplit; fi
}

parse_array () {
  local index=0
  local ary=''
  read -r token
  case "$token" in
    ']') ;;
    *)
      while :
      do
        parse_value "$1" "$index"
        index=$((index+1))
        ary="$ary""$value" 
        read -r token
        case "$token" in
          ']') break ;;
          ',') ary="$ary," ;;
          *) throw "EXPECTED , or ] GOT ${token:-EOF}" ;;
        esac
        read -r token
      done
      ;;
  esac
  [ "$BRIEF" -eq 0 ] && value=$(printf '[%s]' "$ary") || value=
  :
}

parse_object () {
  local key
  local obj=''
  read -r token
  case "$token" in
    '}') ;;
    *)
      while :
      do
        case "$token" in
          '"'*'"') key=$token ;;
          *) throw "EXPECTED string GOT ${token:-EOF}" ;;
        esac
        read -r token
        case "$token" in
          ':') ;;
          *) throw "EXPECTED : GOT ${token:-EOF}" ;;
        esac
        read -r token
        parse_value "$1" "$key"
        obj="$obj$key:$value"        
        read -r token
        case "$token" in
          '}') break ;;
          ',') obj="$obj," ;;
          *) throw "EXPECTED , or } GOT ${token:-EOF}" ;;
        esac
        read -r token
      done
    ;;
  esac
  [ "$BRIEF" -eq 0 ] && value=$(printf '{%s}' "$obj") || value=
  :
}

parse_value () {
  local jpath="${1:+$1,}$2" isleaf=0 isempty=0 print=0
  case "$token" in
    '{') parse_object "$jpath" ;;
    '[') parse_array  "$jpath" ;;
    # At this point, the only valid single-character tokens are digits.
    ''|[!0-9]) throw "EXPECTED value GOT ${token:-EOF}" ;;
    *) value=$token
       # if asked, replace solidus ("\/") in json strings with normalized value: "/"
       [ "$NORMALIZE_SOLIDUS" -eq 1 ] && value=$(echo "$value" | sed 's#\\/#/#g')
       isleaf=1
       [ "$value" = '""' ] && isempty=1
       ;;
  esac
  [ "$value" = '' ] && return
  [ "$NO_HEAD" -eq 1 ] && [ -z "$jpath" ] && return

  [ "$LEAFONLY" -eq 0 ] && [ "$PRUNE" -eq 0 ] && print=1
  [ "$LEAFONLY" -eq 1 ] && [ "$isleaf" -eq 1 ] && [ $PRUNE -eq 0 ] && print=1
  [ "$LEAFONLY" -eq 0 ] && [ "$PRUNE" -eq 1 ] && [ "$isempty" -eq 0 ] && print=1
  [ "$LEAFONLY" -eq 1 ] && [ "$isleaf" -eq 1 ] && \
    [ $PRUNE -eq 1 ] && [ $isempty -eq 0 ] && print=1
  [ "$print" -eq 1 ] && printf "[%s]\t%s\n" "$jpath" "$value"
  :
}

parse () {
  read -r token
  parse_value
  read -r token
  case "$token" in
    '') ;;
    *) throw "EXPECTED EOF GOT $token" ;;
  esac
}

if ([ "$0" = "$BASH_SOURCE" ] || ! [ -n "$BASH_SOURCE" ]);
then
  parse_options "$@"
  tokenize | parse
fi

# vi: expandtab sw=2 ts=2
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to download stuff

_bes_trace_file "begin"

# Download a url to a file with optional username and password.
# uses curl or wget dependning on which one is found
function bes_download()
{
  if [[ $# < 2 ]]; then
    bes_message "Usage: bes_download url filename <username> <password>"
    return 1
  fi
  local _url="${1}"
  shift
  local _filename="${1}"
  shift
  local _username
  local _password
  if [[ $# > 0 ]]; then
    shift
    _username="${1}"
  fi
  if [[ $# > 0 ]]; then
    shift
    _password="${1}"
  fi
  local _dirname="$(dirname ${_filename})"
  mkdir -p ${_dirname}
  local _rv

  if $(bes_has_program curl); then
    _bes_download_curl "${_url}" "${_filename}" "${_username}" "${_password}"
    _rv=$?
    return ${_rv}
  fi
  
  if $(bes_has_program wget); then
    _bes_download_wget "${_url}" "${_filename}" "${_username}" "${_password}"
    _rv=$?
    return ${_rv}
  fi

  bes_message "bes_download: no curl or wget found."
  
  return 1
}

function _bes_download_curl()
{
  if [[ $# < 4 ]]; then
    bes_message "Usage: _bes_download_curl url filename <username> <password>"
    return 1
  fi
  local _url="${1}"
  local _filename="${2}"
  local _username="${3}"
  local _password="${4}"
  local _auth_args
  if [[ -n "${_username}" && -n "${_password}" ]]; then
    _auth_args="--user ${_username}:${_password}"
  else
    _auth_args=""
  fi
  local _http_code=$(curl ${_auth_args} ${_url} --location --output ${_filename} -w "%{http_code}\n" 2> /dev/null)
  if [[ "${_http_code}" != "200" ]]; then
    return 1
  fi
  return 0
}

function _bes_download_wget()
{
  if [[ $# < 4 ]]; then
    bes_message "Usage: _bes_download_wget url filename <username> <password>"
    return 1
  fi
  local _url="${1}"
  local _filename="${2}"
  local _username="${3}"
  local _password="${4}"
  local _auth_args
  if [[ -n "${_username}" && -n "${_password}" ]]; then
    _auth_args="--user ${_username} --password ${_password}"
  else
    _auth_args=""
  fi

  # FIXME: need more error checking here
  wget --quiet --hsts-file /dev/null ${_auth_args} ${_url} -O ${_filename}
  local _rv=$?
  if [[ ${_rv} != 0 ]]; then
    return 1
  fi
  if [[ -f ${_filename} ]]; then
    return 0
  fi
  return 1
}

_bes_trace_file "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file path "begin"

# print the file size in bytes
function bes_file_size()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_file_size filename"
    return 1
  fi
  local _filename="${1}"
  local _file_size=$(wc -c < "${_filename}" | tr -d ' ')
  echo "${_file_size}"
  return 0
}

# print the normalized dir
function bes_dir_normalize()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_dir_normalize dir"
    return 1
  fi
  local _dir="${1}"
  if [[ ! -e "${_dir}" ]]; then
    bes_message "bes_dir_normalize: Directory not found: ${_dir}"
    return 0
  fi
  if [[ ! -d "${_dir}" ]]; then
    bes_message "bes_dir_normalize: Not a directory: ${_dir}"
    return 0
  fi
  local _normalized_dir="$(command cd -P "${_dir}" > /dev/null && command pwd -P )"
  echo "${_normalized_dir}"
  return 0
}

# Determine the normalized directory for a file taking symlinks into account.
function bes_file_dir()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_file_dir filename"
    return 1
  fi
  local _filename="${1}"
  local _resolved_filename
  if [[ -h "${_filename}" ]]; then
    _resolved_filename="$(command readlink "${_filename}" )"
  else
    _resolved_filename="${_filename}"
  fi
  local _file_dir="${_resolved_filename%/*}"
  if [[ "${_file_dir}" == "${_resolved_filename}" ]]; then
    _file_dir=.
  fi
  local _normalized_file_dir="$(bes_dir_normalize "${_file_dir}")"
  echo "${_normalized_file_dir}"
  return 0
}

# check that a file exists or print a message
function bes_file_check()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_file_check label"
    return 1
  fi
  local _label=${FUNCNAME[1]}
  local _filename="${1}"
  if [[ ! -e "${_filename}" ]]; then
    bes_message "${_label}: not found: ${_filename}"
    exit 1
  fi
  return 0
}

bes_log_trace_file path "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file path "begin"

# return just the extension of a file
function bes_filename_extension()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_filename_extension filename"
    return 1
  fi
  local _filename="${1}"
  local _base=$($_BES_BASENAME_EXE -- "${_filename}")
  local _ext="${_base##*.}"
  echo "${_ext}"
  return 0
}

bes_log_trace_file path "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_import "bes_string.bash"

_bes_trace_file "begin"

_BES_GIT_LOG_FILE=${BES_GIT_LOG_FILE:-/dev/null}

# Return 0 if ${1} (or pwd if not given) is a bare git repo
function bes_git_is_bare_repo()
{
  if [[ $# -ge 1 ]]; then
    local _path="${1}"
  else
    local _path="$(pwd)"
  fi
  if [[ ! -f "${_path}"/HEAD ]]; then
    return 1
  fi
  if [[ ! -f "${_path}"/config ]]; then
    return 1
  fi
  if [[ ! -d "${_path}"/refs ]]; then
    return 1
  fi
  if [[ ! -d "${_path}"/objects ]]; then
    return 1
  fi
  return 0
}

# Return 0 if ${1} (or pwd if not given) is a git repo
function bes_git_is_repo()
{
  if [[ $# -ge 1 ]]; then
    local _path="${1}"
  else
    local _path="$(pwd)"
  fi
  if bes_git_is_bare_repo "${_path}"/.git; then
    return 0
  fi
  return 1
}

# Return 0 if ${1} (or pwd if not given) is either a working or bare git repo
function bes_git_is_any_repo()
{
  if [[ $# -ge 1 ]]; then
    local _path="${1}"
  else
    local _path="$(pwd)"
  fi
  if bes_git_is_repo "${_path}"; then
    return 0
  fi
  if bes_git_is_bare_repo "${_path}"; then
    return 0
  fi
  return 1
}

# Return 0 if git repo is clean with no uncommitted or unpushed changes.
function bes_git_repo_is_clean()
{
  if [[ $# -ge 1 ]]; then
    local _path="${1}"
  else
    local _path="$(pwd)"
  fi
  if ! bes_git_is_repo "${_path}"; then
    bes_message "not a git repo: ${_path}"
    return 1
  fi
  if bes_git_repo_has_uncommitted_changes "${_path}"; then
    bes_message "not clean - uncommitted changes: ${_path}"
    return 1
  fi
  if bes_git_repo_has_unpushed_changes "${_path}"; then
    bes_message "not clean - unpushed changes: ${_path}"
    return 1
  fi
  return 0
}

# Return 0 if git repo is clean with no uncommitted or unpushed changes.
function bes_git_non_bare_repo_is_clean()
{
  if [[ $# -ge 1 ]]; then
    local _path="${1}"
  else
    local _path="$(pwd)"
  fi
  if bes_git_is_bare_repo "${_path}"; then
    return 0
  fi
  if ! bes_git_is_repo "${_path}"; then
    bes_message "not a git repo: ${_path}"
    return 1
  fi
  if bes_git_repo_has_uncommitted_changes "${_path}"; then
    bes_message "not clean - uncommitted changes: ${_path}"
    return 1
  fi
  if bes_git_repo_has_unpushed_changes "${_path}"; then
    bes_message "not clean - unpushed changes: ${_path}"
    return 1
  fi
  return 0
}

# Return 0 if git repo has uncommited changes
function bes_git_repo_has_uncommitted_changes()
{
  if [[ $# -ge 1 ]]; then
    local _path="${1}"
  else
    local _path="$(pwd)"
  fi

  if bes_git_is_bare_repo "${_path}"; then
    return 0
  fi

  if ! bes_git_is_repo "${_path}"; then
    return 1
  fi
  if $(cd "${_path}" && ${BES_GIT_EXE:-git} diff-index --quiet HEAD --); then
    return 1
  fi
  return 0
}

# Return 0 if git repo has untracked files
function bes_git_repo_has_untracked_files()
{
  if [[ $# -ge 1 ]]; then
    local _path="${1}"
  else
    local _path="$(pwd)"
  fi

  if bes_git_is_bare_repo "${_path}"; then
    return 1
  fi

  if ! bes_git_is_repo "${_path}"; then
    return 1
  fi
  local _num=$(cd "${_path}" && ${BES_GIT_EXE:-git} status --untracked=all --porcelain | grep "?? " | wc -l)
  if [[ $(expr ${_num}) > 0 ]]; then
    return 0
  fi
  return 1
}

# Return 0 if git repo has uncommited changes
function bes_git_repo_has_unpushed_changes()
{
  if [[ $# -ge 1 ]]; then
    local _repo="${1}"
  else
    local _repo="$(pwd)"
  fi
  if ! bes_git_is_repo "${_repo}"; then
    return 1
  fi
  local _cherries=$(bes_git_call "${_repo}" cherry | grep -E '^\+\s[a-f0-9]+$' | wc -l)
  if [[ ${_cherries} -ne 0 ]]; then
    return 0
  fi
  return 1
}

# Call git with a specific root
function bes_git_call()
{
  if [[ $# < 1 ]]; then
    echo "usage: bes_git_call repo <args>"
    return 1
  fi
  local _repo="${1}"
  shift
  ( cd "${_repo}" && ${BES_GIT_EXE:-git} ${1+"$@"} )
  return $?
}

function bes_git_local_branch_exists()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_local_branch_exists root branch_name"
    return 1
  fi
  local _root="${1}"
  local _branch_name="${2}"
  if bes_git_call "${_root}" branch | sed -E 's/^\*/ /' | awk '{ print $1; }' | grep -w ${_branch_name} >& "${_BES_GIT_LOG_FILE}"; then
    return 0
  fi
  return 1
}

function bes_git_local_branch_delete()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_local_branch_delete root branch_name"
    return 1
  fi
  local _root="${1}"
  local _branch_name="${2}"
  if bes_git_local_branch_exists "${_root}" ${_branch_name}; then
    bes_git_call "${_root}" branch --delete ${_branch_name}
  fi
  return 0
}

function bes_git_remote_is_added()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_git_remote_is_added root remote_name"
    return 1
  fi
  local _root="${1}"
  local _remote_name=${2}
  if bes_git_call "${_root}" ls-remote --exit-code ${_remote_name} >& "${_BES_GIT_LOG_FILE}"; then
    return 0
  fi
  return 1
}

function bes_git_remote_remove()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_git_remote_remove root remote_name"
    return 1
  fi
  local _root="${1}"
  local _remote_name=${2}
  if bes_git_remote_is_added "${_root}" ${_remote_name}; then
    bes_git_call "${_root}" remote remove ${_remote_name}
  fi
  return 0
}  

function bes_git_last_commit_hash()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_git_last_commit_hash repo <short_hash>"
    return 1
  fi
  local _repo="${1}"
  local _long_hash=$(bes_git_call "${_repo}" log --format=%H -n 1)
  local _want_short_hash="false"
  if [[ $# > 1 ]]; then
    _want_short_hash=${2}
  fi
  if [[ ${_want_short_hash} == "true" ]]; then
    _hash=$(bes_git_short_hash "${_repo}" ${_long_hash})
  else
    _hash=${_long_hash}
  fi
  echo ${_hash}
  return 0
}  

# return the commit hash for ref
function bes_git_commit_for_ref()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_git_commit_for_ref root_dir ref <short_hash>"
    return 1
  fi
  local _root_dir="${1}"
  shift
  local _ref="${1}"
  shift
  local _short_hash="false"
  if [[ $# > 1 ]]; then
    _short_hash=${1}
  fi
  local _long_hash=$(bes_git_call "${_root_dir}" rev-list -n 1 ${_ref})
  if [[ ${_short_hash} == "true" ]]; then
    _hash=$(bes_git_short_hash "${_root_dir}" ${_long_hash})
  else
    _hash=${_long_hash}
  fi
  echo ${_hash}
  return 0
}  

# return the commit hash to which the submodule points
function bes_git_submodule_revision()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_git_submodule_commit repo submodule <short_hash>"
    return 1
  fi
  local _repo="${1}"
  local _submodule="${2}"
  local _want_short_hash="false"
  if [[ $# > 2 ]]; then
    _want_short_hash=${3}
  fi
  local _hash
  local _long_hash=$(bes_git_call "${_repo}" ls-tree HEAD "${_submodule}" | awk '$2 == "commit"' | awk '{ print $3; }')
  if [[ ${_want_short_hash} == "true" ]]; then
    _hash=$(bes_git_short_hash "${_repo}/${_submodule}" ${_long_hash})
  else
    _hash=${_long_hash}
  fi
  echo ${_hash}
  return 0
}

# init a submodule.  optional recursive argument
function bes_git_submodule_init()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_git_submodule_init submodule [recursive]"
    return 1
  fi
  
  if bes_git_repo_has_uncommitted_changes; then
    bes_message "bes_git_submodule_init: The git tree needs to be clean with no uncommitted changes."
    return 1
  fi
  local _submodule="${1}"
  local _recursive_flag=""
  if [[ $# > 1 ]]; then
    if [[ ${2} == "true" ]]; then
      _recursive_flag="--recursive"
    fi
  fi
  ${BES_GIT_EXE:-git} submodule update --init ${_recursive_flag} "${_submodule}"
  return 0
}

# update a submodule to the given revision or HEAD if none is given
# commit the result with a meaningful message
# update is *NOT* recursive.  only the top level submodule is updated
function bes_git_submodule_update()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_git_submodule_update repo submodule [revision]"
    return 1
  fi
  local _repo="${1}"
  shift
  if bes_git_repo_has_uncommitted_changes "${_repo}"; then
    bes_message "bes_git_submodule_update: The git tree needs to be clean with no uncommitted changes: ${_repo}"
    return 1
  fi
  local _submodule=${1}
  shift
  local _revision="HEAD"
  if [[ $# > 0 ]]; then
    _revision=${1}
  fi
    
  local _old_revision=$(bes_git_submodule_revision "${_repo}" ${_submodule} true)
  ( cd "${_repo}" && ${BES_GIT_EXE:-git} submodule update --init ${_submodule} )
  ( cd "${_repo}" && ${BES_GIT_EXE:-git} submodule update --remote --merge ${_submodule} )
  local _new_revision=$(bes_git_last_commit_hash "${_repo}/${_submodule}" true)
  if [[ ${_old_revision} == ${_new_revision} ]]; then
    bes_message "submodule ${_submodule} already at latest revision ${_new_revision}"
    return 0
  fi
  ( cd "${_repo}" && ${BES_GIT_EXE:-git} add ${1} )
  local _message="submodule ${_submodule} updated from ${_old_revision} to ${_new_revision}"
  ( cd "${_repo}" && ${BES_GIT_EXE:-git} commit -m"${_message}" . )
  bes_message "${_message}"
  return 0
}

function bes_git_short_hash()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_git_short_hash repo long_hash"
    return 1
  fi
  local _repo="${1}"
  local _long_hash=${2}
  local _short_hash=$(bes_git_call "${_repo}" rev-parse --short ${_long_hash})
  echo ${_short_hash}
  return 0
}

function bes_git_pack_size()
{
  if [[ $# > 1 ]]; then
    bes_message "usage: bes_git_pack_size <repo>"
    return 1
  fi
  local _repo=
  if [[ $# == 1 ]]; then
    _repo="${1}"
  else
    _repo="$(pwd)"
  fi
  local _pack_size=$(bes_git_call "${_repo}" count-objects -v | grep size-pack  | awk '{ print $2; }')
  echo ${_pack_size}
  return 0
}

# gc strategy published by bfg docs
function bes_git_gc()
{
  if [[ $# > 1 ]]; then
    bes_message "usage: bes_git_gc <repo>"
    return 1
  fi
  local _repo=
  if [[ $# == 1 ]]; then
    _repo="${1}"
  else
    _repo="$(pwd)"
  fi
  local _pack_size_before=$(bes_git_pack_size "${_repo}")
  local _gc_log="$(pwd)"/gc.log
  ( cd "${_repo}" && ${BES_GIT_EXE:-git} reflog expire --expire=now --all && ${BES_GIT_EXE:-git} gc --prune=now --aggressive ) >& ${_gc_log}
  local _pack_size_after=$(bes_git_pack_size "${_repo}")
  bes_message "bes_git_gc: delta: before=${_pack_size_before} after=${_pack_size_after} gc_log=${_gc_log}"
  return 0
}

# gc strategy published by atlassian bitbucket
function bes_git_gc2()
{
  if [[ $# > 1 ]]; then
    bes_message "usage: bes_git_gc2 <repo>"
    return 1
  fi
  local _repo=
  if [[ $# == 1 ]]; then
    _repo="${1}"
  else
    _repo="$(pwd)"
  fi
  local _pack_size_before=$(bes_git_pack_size "${_repo}")
  local _gc_log="$(pwd)"/gc.log
  bes_git_call "${_repo}" \
      -c gc.auto=1 \
      -c gc.autodetach=false \
      -c gc.autopacklimit=1 \
      -c gc.garbageexpire=now \
      -c gc.reflogexpireunreachable=now \
      gc --prune=all >& ${_gc_log}
  local _pack_size_after=$(bes_git_pack_size "${_repo}")
  bes_message "bes_git_gc: delta: before=${_pack_size_before} after=${_pack_size_after} gc_log=${_gc_log}"
  return 0
}

# Return true (0) if the repo has git lfs files
function bes_git_repo_has_lfs_files()
{
  local _repo=
  if [[ $# == 1 ]]; then
    _repo="${1}"
  else
    _repo="$(pwd)"
  fi
  local _n=$(bes_git_call "${_repo}" lfs ls-files | wc -l | awk '{ print $1; }')
  if [[ ${_n} != 0 ]]; then
    return 0
  fi
  return 1
}

# Return true (0) if a git lfs file needs pulling
function bes_git_lfs_file_needs_pull()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_lfs_file_needs_pull repo filename"
    return 1
  fi
  local _repo="${1}"
  local _filename="${2}"
  local _found=$(cd "${_repo}" && ${BES_GIT_EXE:-git} lfs ls-files | grep -w "${_filename}")
  if [[ -z "${_found}" ]]; then
    bes_message "lfs file ${_filename} not found in ${_repo}"
    return 1
  fi
  local _status=$(echo "${_found}" | awk '{ print $2; }')
  if [[ ${_status} == "*" ]]; then
    return 1
  fi
  return 0
}

# Return all the remote tags ordered by software version
function bes_git_list_remote_tags()
{
  if [[ $# != 1 ]]; then
    echo "usage: bes_git_list_remote_tags root_dir"
    return 1
  fi
  local _root_dir="${1}"
  if ! bes_git_is_repo "${_root_dir}"; then
    bes_message "not a git repo: ${_root_dir}"
    return 1
  fi
  bes_git_call "${_root_dir}" \
    ls-remote --tags 2> "${_BES_GIT_LOG_FILE}" | \
    awk '{ print $2; }' | \
    sed 's/refs\/tags\///' | \
    sed 's/\^{}//' | \
    sort -V | \
    uniq
  return 0
}

function bes_git_greatest_remote_tag()
{
  if [[ $# != 1 ]]; then
    echo "usage: bes_git_greatest_remote_tag root_dir"
    return 1
  fi
  local _root_dir="${1}"
  if ! bes_git_is_repo "${_root_dir}"; then
    bes_message "not a git repo: ${_root_dir}"
    return 1
  fi
  bes_git_list_remote_tags "${_root_dir}" | tail -1
  return 0
}

function bes_git_has_remote_tag()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_has_remote_tag root_dir tag"
    return 1
  fi
  local _root_dir="${1}"
  local _tag="${2}"
  if bes_git_list_remote_tags "${_root_dir}" | grep ${_tag} >& "${_BES_GIT_LOG_FILE}"; then
    return 0
  fi
  return 1
}

function bes_git_tag()
{
  if [[ $# < 2 ]]; then
    echo "usage: bes_git_tag root_dir tag_name <commit>"
    return 1
  fi
  local _root_dir="${1}"
  shift
  local _tag_name="${1}"
  shift
  local _commit=
  if [[ $# > 1 ]]; then
    _commit=${1}
  fi
  
  if ! bes_git_is_repo "${_root_dir}"; then
    bes_message "not a git repo: ${_root_dir}"
    return 1
  fi
  if bes_git_has_remote_tag "${_root_dir}" ${_tag_name}; then
    bes_message "tag already exists in remote: ${_tag_name}"
    return 1
  fi
  bes_git_call "${_root_dir}" tag ${_tag_name} ${_commit} >& "${_BES_GIT_LOG_FILE}"
  bes_git_call "${_root_dir}" push origin ${_tag_name} >& "${_BES_GIT_LOG_FILE}"
  bes_git_call "${_root_dir}" fetch --tags >& "${_BES_GIT_LOG_FILE}"
  return 0
}

# Return all the remote tags that start with prefix
function bes_git_list_remote_prefixed_tags()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_list_remote_prefixed_tags root_dir prefix"
    return 1
  fi
  local _root_dir="${1}"
  local _prefix="${2}"
  
  if ! bes_git_is_repo "${_root_dir}"; then
    bes_message "not a git repo: ${_root_dir}"
    return 1
  fi

  local _all_tags=( $(bes_git_list_remote_tags ${_root_dir}) )
  local _tag
  for _tag in "${_all_tags[@]}"; do
    if bes_str_starts_with ${_tag} ${_prefix}; then
      echo ${_tag}
    fi
  done
  return 0
}

function bes_git_greatest_remote_prefixed_tag()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_greatest_remote_prefixed_tag root_dir prefix"
    return 1
  fi
  local _root_dir="${1}"
  local _prefix="${2}"
  
  if ! bes_git_is_repo "${_root_dir}"; then
    bes_message "not a git repo: ${_root_dir}"
    return 1
  fi
  
  bes_git_list_remote_prefixed_tags "${_root_dir}" ${_prefix} | tail -1
  
  return 0
}

function bes_git_repo_commit_for_ref()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_git_repo_commit_for_ref address ref"
    return 1
  fi
  local _address=${1}
  local _ref=${2}
  local _tmp=/tmp/bes_git_repo_commit_for_ref_$$
  rm -rf "${_tmp}"
  mkdir -p "${_tmp}"
  ${BES_GIT_EXE:-git} clone ${_address} "${_tmp}" >& "${_BES_GIT_LOG_FILE}"
  local _commit_hash=$(bes_git_commit_for_ref "${_tmp}" ${_ref})
  rm -rf "${_tmp}"
  echo ${_commit_hash}
  return 0
}

# print the latest tag in a repo by address
function bes_git_repo_latest_tag()
{
  if [[ $# != 1 ]]; then
    bes_message "usage: bes_git_repo_latest_tag address"
    return 1
  fi
  local _address=${1}
  local _tmp=/tmp/bes_git_repo_latest_tag_$$
  rm -rf "${_tmp}"
  mkdir -p "${_tmp}"
  git clone ${_address} "${_tmp}" >& /dev/null
  local _latest_tag=$(cd "${_tmp}" && git tag -l | sort -V | tail -1)
  rm -rf "${_tmp}"
  echo ${_latest_tag}
  return 0
}

# Print the date for commit
function bes_git_commit_date()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_commit_message root_dir ref"
    return 1
  fi
  local _root_dir="${1}"
  local _commit="${2}"
  local _message=$(bes_git_call "${_root_dir}" log -n 1 --format=%ai ${_commit})
  echo ${_message}
  return 0
}

# Print the message for commit
function bes_git_commit_message()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_git_commit_message root_dir ref"
    return 1
  fi
  local _root_dir="${1}"
  local _commit="${2}"
  local _message=$(bes_git_call "${_root_dir}" log -n 1 --pretty=format:%s ${_commit})
  echo ${_message}
  return 0
}

_bes_trace_file "end"
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

  local _tmp_dir="$(mktemp -d)/bes_git_subtree_update_tmp-${_my_name}-$$"
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
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

_bes_trace_file "begin"

function bes_json_file_parse()
{
  if [[ $# < 1 ]]; then
    bes_message "Usage: bes_json_parse_file filename <args>"
    return 1
  fi
  local _filename="${1}"
  shift
  local _this_dir=$(echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")
  local _json_parser="${_this_dir}/bes_dominictarr_json.bash"

  "${_json_parser}" ${1+"$@"} < "${_filename}"
  local _exit_code=$?
  return ${_exit_code}
}

function bes_json_file_get_field()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: bes_json_file_get_field filename field"
    return 1
  fi
  local _filename="${1}"
  local _field="${2}"

  bes_json_file_parse "${_filename}" -b | grep -w "${_field}" | awk -F"\t" '{ print $2; }' | tr -d '"'
  local _exit_code=$?
  return ${_exit_code}
}

_bes_trace_file "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file list "begin"

# Return 0 if the first argument is in any of the following arguments
function bes_is_in_list()
{
  if [[ $# < 1 ]]; then
    printf "\nUsage: bes_is_in_list what l1 l2 ... lN\n\n"
    return 1
  fi
  local _what="$1"
  shift
  local _next
  while [[ $# > 0 ]]; do
    _next="$1"
    if [[ "$_what" == "$_next" ]]; then
      return 0
    fi
    shift
  done
  return 1
}

bes_log_trace_file path "end"

#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_import "bes_list.bash"
bes_import "bes_string.bash"
bes_import "bes_system.bash"

bes_log_trace_file path "begin"

# return a colon separated path without the head item
function bes_path_without_head()
{
  local _path="$*"
  local _head=${_path%%:*}
  local _without_head=${_path#*:}
  if [[ "${_without_head}" == "${_head}" ]]; then
    _without_head=""
  fi
  echo ${_without_head}
  return 0
}

# return just the head item of a colon separated path
function bes_path_head()
{
  local _path="$*"
  local _head=${_path%%:*}
  echo ${_head}
  return 0
}

# Strip rogue colon(s) from head of path
function bes_path_head_strip_colon()
{
  local _path="$*"
  local _result="${_path#:}"
  while [[ "${_result}" != "${_path}" ]]; do
    _path="${_result}"
    _result="${_path#:}"
  done
  echo "${_result}"
  return 0
}

# Strip rogue colon(s) from tail of path
function bes_path_tail_strip_colon()
{
  local _path="$*"
  local _result="${_path%:}"
  while [[ "${_result}" != "${_path}" ]]; do
    _path="${_result}"
    _result="${_path%:}"
  done
  echo "${_result}"
  return 0
}

# Strip rogue colon(s) from head and tail of path
function bes_path_strip_colon()
{
  local _path="$*"
  local _result=$(bes_path_head_strip_colon "${_path}")
  echo $(bes_path_tail_strip_colon "${_result}")
  return 0
}

# Strip rogue slashes from a path
function bes_path_clean_rogue_slashes()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_path_clean_rogue_slashes path"
    return 1
  fi
  local _path="${1}"
  echo "${_path}" | ${_BES_SED} 's#//*#/#g'
  return 0
}

# remove duplicates from a path
# from https://unix.stackexchange.com/questions/14895/duplicate-entries-in-path-a-problem
function bes_path_dedup()
{
  bes_log_trace_function path $*

  if [[ $# != 1 ]]; then
    echo "Usage: bes_path_dedup path"
    return 1
  fi
  local _tmp="$*"
  local _head
  local _result=""
  while [[ -n "$_tmp" ]]; do
    _head=$(bes_path_head "${_tmp}")
    _tmp=$(bes_path_without_head "${_tmp}")
    case ":${_result}:" in
      *":${_head}:"*) :;; # already there
      *) _result="${_result}:${_head}";;
    esac
  done
  echo $(bes_path_strip_colon "${_result}")
  return 0
}

# sanitize a path by deduping entries and stripping leading or trailing colons
function bes_path_sanitize()
{
  if [[ $# -ne 1 ]]; then
    echo "Usage: bes_path_sanitize path"
    return 1
  fi
  local _path="${1}"
  local _r1="$(bes_path_clean_rogue_slashes "${_path}")"
  local _r2="$(bes_path_dedup "${_r1}")"
  local _r3="$(bes_path_strip_colon "${_r2}")"
  echo ${_r3}
  return 0
}

# remove one or more items from a colon delimited path
function bes_path_remove()
{
  bes_log_trace_function path $*

  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_remove path p1 p2 ... pN"
    return 1
  fi
  local _tmp="$1"
  shift
  local _head
  local _result=""
  while [[ -n "$_tmp" ]]; do
    _head=$(bes_path_head "${_tmp}")
    _tmp=$(bes_path_without_head "${_tmp}")
    if ! bes_is_in_list "$_head" "$@"; then
      if [[ -z ${_result} ]]; then
        _result="${_head}"
      else
        _result="${_result}:${_head}"
      fi
    fi
  done
  echo "${_result}"
  return 0
}

# append one or more items to a colon delimited path
function bes_path_append()
{
  bes_log_trace_function path $*

  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_append path p1 p2 ... pN"
    return 1
  fi
  local _left
  IFS=':' read -ra _left <<< "${1}"
  shift
  local _right=()
  local i
  for ((i = 1; i <= ${#}; i++)); do
    _right+=("${!i}")
  done
  local _new_path=()
  for ((i = 0; i < ${#_left[@]}; i++)); do
    _new_path+=("${_left[${i}]}")
  done
  for ((i = 0; i < ${#_right[@]}; i++)); do
    _new_path+=("${_right[${i}]}")
  done
  local _result=$(for ((i = 0; i < ${#_new_path[@]}; i++)); do
    if [[ $i != 0 ]]; then
       printf ":"
    fi
    printf "%s" "${_new_path[${i}]}"
  done)
  bes_path_sanitize "${_result}"
  return 0
}

# prepend one or more items to a colon delimited path
function bes_path_prepend()
{
  bes_log_trace_function path $*

  if [[ $# < 2 ]]; then
    echo "Usage: bes_path_prepend path p1 p2 ... pN"
    return 1
  fi
  bes_log path debug "bes_path_prepend ARGS $*"
  bes_log path debug "bes_path_prepend NUM ${#}"
  local _right
  IFS=':' read -ra _right <<< "${1}"
  bes_log path debug "bes_path_prepend _right=${_right[*]} num=${#_right[*]}"
  shift
  local _left=()
  local i
  bes_log path debug "bes_path_prepend num args ${#}"
  for ((i = 1; i <= ${#}; i++)); do
    _left+=("${!i}")
  done
  bes_log path debug "bes_path_prepend _left=${_left[*]} num=${#_left[*]}"
  local _new_path=()
  for ((i = 0; i < ${#_left[@]}; i++)); do
    _new_path+=("${_left[${i}]}")
  done
  for ((i = 0; i < ${#_right[@]}; i++)); do
    _new_path+=("${_right[${i}]}")
  done
  local _result=$(for ((i = 0; i < ${#_new_path[@]}; i++)); do
    if [[ $i -ne 0 ]]; then
       printf ":"
    fi
    printf "%s" "${_new_path[${i}]}"
  done)
  bes_path_sanitize "${_result}"
  return 0
}

# pretty print a path one item per line including unexpanding ~/
function bes_path_print()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_path_print path"
    return 1
  fi
  local _tmp="$*"
  local _head
  while [[ -n "$_tmp" ]]; do
    _head=$(bes_path_head "${_tmp}")
    _tmp=$(bes_path_without_head "${_tmp}")
    echo ${_head/$HOME/\~}
  done
  return 0
}

function bes_env_path_sanitize()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  local _value=$(bes_var_get ${_var_name})
  local _new_value=$(bes_path_sanitize "$_value")
  bes_var_set ${_var_name} "$_new_value"
  return 0
}

function bes_env_path_append()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  shift
  local _value=$(bes_var_get ${_var_name})
  local _new_value=$(bes_path_append "${_value}" "${@}")
  bes_var_set ${_var_name} "$_new_value"
  export ${_var_name}
  return 0
}

function bes_env_path_prepend()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  shift
  bes_log path debug "bes_env_path_prepend _var_name=${_var_name}"
  local _value=$(bes_var_get ${_var_name})
  bes_log path debug "bes_env_path_prepend _value=${_value}"
  local _new_value=$(bes_path_prepend "${_value}" "${@}")
  bes_var_set ${_var_name} "$_new_value"
  export ${_var_name}
  bes_log path debug "bes_env_path_prepend result ${_new_value}"
  return 0
}

function bes_env_path_remove()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  shift
  local _parts="$@"
  local _value=$(bes_var_get ${_var_name})
  local _new_value=$(bes_path_remove "$_value" "$_parts")
  bes_var_set ${_var_name} "$_new_value"
  export ${_var_name}
  return 0
}

function bes_env_path_clear()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  bes_var_set ${_var_name} ""
  export ${_var_name}
  return 0
}

function bes_env_path_print()
{
  bes_log_trace_function path $*

  local _var_name=$(bes_variable_map $1)
  local _value="$(bes_var_get ${_var_name})"
  bes_path_print "${_value}"
  return 0
}

function _bes_variable_map_macos()
{
  local _var_name=$1
  local _rv
  case ${_var_name} in
    LD_LIBRARY_PATH)
      _rv=DYLD_LIBRARY_PATH
      ;;
    *)
      _rv=${_var_name}
      ;;
  esac
  echo ${_rv}
  return 0
}

function _bes_variable_map_linux()
{
  local _var_name=$1
  local _rv
  case ${_var_name} in
    DYLD_LIBRARY_PATH)
      _rv=LD_LIBRARY_PATH
      ;;
    *)
      _rv=${_var_name}
      ;;
  esac
  echo ${_rv}
  return 0
}

function bes_variable_map()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_variable_map var_name"
    return 1
  fi
  local _uname=$(${_BES_UNAME})
  local _var_name=$1
  local _rv
  case ${_uname} in
    Darwin)
      _rv=$(_bes_variable_map_macos ${_var_name})
      ;;
    Linux|*)
      _rv=$(_bes_variable_map_linux ${_var_name})
      ;;
  esac
  echo ${_rv}
  return 0
}

function LD_LIBRARY_PATH_var_name()
{
  local _uname=$(${_BES_UNAME})
  local _rv=
  case ${_uname} in
    Darwin)
      _rv=DYLD_LIBRARY_PATH
      ;;
    Linux|*)
      _rv=LD_LIBRARY_PATH
      ;;
  esac
  echo $_rv
  return 0
}

# Return 0 if the given path is absolute
function bes_path_is_abs()
{
  if [[ $# != 1 ]]; then
    echo "usage: bes_path_is_abs path"
    return 1
  fi
  local _path="${1}"

  if [[ "${_path}" =~ ^\/.* ]]; then
    return 0
  fi
  return 1
}

# Return 0 if the given path is a symlink
function bes_path_is_symlink()
{
  if [[ $# != 1 ]]; then
    echo "usage: bes_path_is_symlink path"
    return 1
  fi
  local _path="${1}"

  if test -h "${_path}"; then
    return 0
  fi
  return 1
}

function bes_PATH()
{
  bes_env_path_print PATH
}

function bes_PYTHONPATH()
{
  bes_env_path_print PYTHONPATH
}

function bes_LD_LIBRARY_PATH()
{
  bes_env_path_print LD_LIBRARY_PATH
}

# Return the absolute dir path for path.  Note that path will be created
# if it doesnt exist so that this function can be used for paths that
# dont yet exist.  That is useful for scripts that want to normalize
# their file input/output arguments.
function bes_path_abs_dir()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_path_abs_dir path"
    return 1
  fi
  local _path="${1}"
  if [[ ! -d "${_path}" ]]; then
    $_BES_MKDIR_EXE -p "${_path}"
  fi
  local _result="$(cd "${_path}" && $_BES_PWD_EXE)"
  echo ${_result}
  return 0
}

function bes_path_abs_file()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_path_abs_file filename"
    return 1
  fi
  local _filename="${1}"
  local _dirname="$($_BES_DIRNAME_EXE "${_filename}")"
  local _basename="$($_BES_BASENAME_EXE "${_filename}")"
  local _abs_dirname="$(bes_path_abs_dir "${_dirname}")"
  local _result="${_abs_dirname}"/"${_basename}"
  echo ${_result}
  return 0
}

# Split a path by path delimiter
function bes_path_split()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_path_split path"
    return 1
  fi
  local _path="${1}"
  bes_str_split "${_path}" :
  local _rv=$?
  return ${_rv}
}

bes_log_trace_file path "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file pip_project "begin"

bes_import "bes_checksum.bash"

function bes_pip_project_requirements_are_stale()
{
  if [[ $# < 2 ]]; then
    echo "Usage: bes_pip_project_requirements_are_stale project_root_dir reqs_file1 .. reqs_fileN"
    return 1
  fi
  local _project_root_dir="${1}"
  shift
  local _requirements_filename
  for _requirements_filename in $@; do
    local _basename=$(basename "${_requirements_filename}")
    local _checksum_filename="${_project_root_dir}/.requirements_checksums/${_basename}"
    if ! bes_checksum_check_file "${_requirements_filename}" "${_checksum_filename}"; then
      return 0
    fi
  done
  return 1
}

bes_log_trace_file pip_project "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to deal with python

bes_import "bes_download.bash"
bes_import "bes_path.bash"
bes_import "bes_string.bash"
bes_import "bes_system.bash"

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

# Find the default python preferring the latest 3.x
function bes_python_find_default()
{
  local _possible_python
  for _possible_version in 3.10 3.9 3.8 3.7 3 2.7; do
    if bes_has_python ${_possible_version}; then
      local _python_exe="$(${_BES_WHICH_EXE} python${_possible_version})"
      echo ${_python_exe}
      return 0
    fi
  done
  echo ""
  return 1
}

# Find python by version
function bes_python_find()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_python_find version"
    return 1
  fi
  local _version=${1}
  local _exe=$(_bes_python_find_check_version ${_version})
  local _rv=$?
  echo ${_exe}
  return ${_rv}
}

# Find python by version ($major.$minor)
function _bes_python_find_by_major_minor_version()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_python_find_by_major_minor_version version"
    return 1
  fi
  local _version=${1}
  local _searchPATH="$(_bes_python_exe_search_path)"
  local _possible_python=python${_version}
  local _python_exe
  if _python_exe=$(PATH="${_searchPATH}" ${_BES_WHICH_EXE} ${_possible_python}); then
    echo "${_python_exe}"
    return 0
  fi
  echo ""
  return 1
}

# Find python by checking the version of the possible python executables
function _bes_python_find_check_version()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_python_find_caca version"
    return 1
  fi
  local _version=${1}
  local _searchPATH="$(_bes_python_exe_search_path)"
  declare -a _path
  local _path_entry
  IFS=':' read -ra _path <<< "${_searchPATH}"
  for _path_entry in "${_path[@]}"; do
    if [[ -d "${_path_entry}" ]]; then
      local _exes=( $(_bes_python_possible_exes_in_dir "${_path_entry}") )
      local _next_exe
      for _next_exe in ${_exes[@]}; do
        local _next_version=$(bes_python_exe_version "${_next_exe}")
        if [[ ${_next_version} == ${_version} ]]; then
          echo ${_next_exe}
          return 0
        fi
      done
    fi
  done
  echo ""
  return 0
}

function _bes_python_possible_exes_in_dir()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: _bes_python_possible_exes_in_dir dir"
    return 1
  fi
  local _dir="${1}"
  declare -a _exes
  local _exes=()
  local _possible_patterns=( python3.[0-9] python3.[0-9][0-9] python3 python2.[0-9] python2 python )
  local _pattern
  
  for _pattern in ${_possible_patterns[*]}; do
    local _next_exes
    if _next_exes=$(cd "${_dir}" && "${_BES_LS}" -1 ${_pattern} 2> /dev/null); then
      local _next_exe
      for _next_exe in ${_next_exes}; do
        _exes+=( "${_dir}/${_next_exe}" )
      done
    fi
  done
  echo ${_exes[@]}
  return 0
}

function _bes_python_exe_search_path()
{
  local _possiblePATH=($(_bes_python_possible_bin_dirs))
  local _searchPATH=$(bes_path_prepend "${PATH}" ${_possiblePATH[@]})
  local _sanitizedPATH=$(bes_path_sanitize "${_searchPATH}")
  echo "${_sanitizedPATH}"
  return 0
}

function _bes_python_possible_bin_dirs()
{
  local _system=$(bes_system)
  local _rv=1
  local _dirs=()
  case ${_system} in
    linux)
      _dirs=$(_bes_python_possible_bin_dirs_linux)
      _rv=$?
      ;;
    macos)
      _dirs=$(_bes_python_possible_bin_dirs_macos)
      _rv=$?
      ;;
    windows)
      _dirs=$(_bes_python_possible_bin_dirs_windows)
      _rv=$?
      ;;
    *)
      bes_message "Unsupported system: ${_system}"
      ;;
  esac
  echo "${_dirs[@]}"
  return ${_rv}
}

function _bes_python_possible_bin_dirs_linux()
{
  local _dirs=()
  _dirs+=(/usr/bin /usr/local/bin /opt/local/bin)
  echo ${_dirs[@]}
  return 0
}

function _bes_python_possible_bin_dirs_macos()
{
  local _dirs=()
  _dirs+=($(echo /usr/local/opt/python@3.*/bin))
  _dirs+=(/opt/local/bin /usr/bin /usr/local/bin)
  echo ${_dirs[@]}
  return 0
}

function _bes_python_possible_bin_dirs_windows()
{
  local _dirs=()
  _dirs+=(/opt/local/bin /usr/bin /usr/local/bin)
  _dirs+=($(echo /usr/local/opt/python@3.*))
  echo ${_dirs[@]}
  return 0
}

_bes_trace_file "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to ask questions

_bes_trace_file "begin"

function bes_question_yes_no()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_question_yes_no var_name message"
    return 1
  fi
  local _CHOICES="[y]es [n]o"
  local _var_name="${1}"
  local _message="${2}"
  local _local_answer
  local _result=1
  while true; do
    read -p "${_message} - ${_CHOICES}: " _local_answer
    case "${_local_answer}" in
      y|Y|yes|YES)
        _result=yes
        break
        ;;
      n|N|no|NO)
        _result=no
        break
        ;;
      *)
        bes_message "Invalid answer: ${_local_answer}.  Please answer: ${_CHOICES}"
    esac
  done
  eval ${_var_name}=${_result}
  return 0
}

_bes_trace_file "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to deal with strings

bes_log_trace_file path "begin"

# Strip whitespace from the head of a string
# From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
function bes_str_strip_head()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_strip_head str"
    return 1
  fi
  local _str="${1}"
  local _stripped="$(echo -e "${_str}" | sed -e 's/^[[:space:]]*//')"
  echo "${_stripped}"
  return 0
}

# Strip whitespace from the tail of a string
# From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
function bes_str_strip_tail()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_strip_head str"
    return 1
  fi
  local _str="${1}"
  local _stripped="$(echo -e "${_str}" | sed -e 's/[[:space:]]*$//')"
  echo "${_stripped}"
  return 0
}

# Strip whitespace from both the head and tail of a string
# From https://stackoverflow.com/questions/369758/how-to-trim-whitespace-from-a-bash-variable
function bes_str_strip()
{
  if [[ $# != 1 ]]; then
    bes_message "Usage: bes_strip_head str"
    return 1
  fi
  local _str="${1}"
  local _stripped="$(echo -e "${_str}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  echo "${_stripped}"
  return 0
}

# Partition a string into left, separator and right.
# delimiter needs to be single char
# the result is 3 lines:
#  left
#  delimiter
#  right
# if no delimiter is found then the result is:
#  str
#
#
# you can either use "head" and "tail" on the results to get the parts you
# need or use arrays like this:
# foo=( "$(bes_str_partition "  key: value with spaces" ":")" )
function bes_str_partition()
{
  if [[ $# != 2 ]]; then
    bes_message "Usage: bes_str_partition str delimiter"
    return 1
  fi
  local _str="${1}"
  local _delimiter=${2}
  if [[ ${#_delimiter} != 1 ]]; then
    bes_message "bes_str_partition: delimiter should be a single char: \"${_delimiter}\""
    return 1
  fi
  local _left="$(echo "${_str}" | cut -d${_delimiter} -f 1)"
  local _right
  local _delimiter_result
  if [[ "${_left}" != "${_str}" ]]; then
    local _left_len=$(echo ${#_left})
    local _cut_index=$(( _left_len + 2 ))
    _right="$(echo "${_str}" | cut -b${_cut_index}-)"
    _delimiter_result=${_delimiter}
  fi

  echo "${_left}"
  echo "${_delimiter_result}"
  echo "${_right}"
  
  return 0
}

# Convert a single argument string to lower case
function bes_str_to_lower()
{
  local _result=$( echo "$@" | $_BES_TR_EXE '[:upper:]' '[:lower:]' )
  echo ${_result}
  return 0
}

function bes_str_split()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_str_split string delimiter"
    return 1
  fi
  local _string="${1}"
  local _delimiter="${2}"
  local _saveIFS="${IFS}"
  local _result
  IFS="${_delimiter}" read -r -a _result <<< "${_string}"
  echo "${_result[@]}"
  IFS="${_saveIFS}"
  return 0
}

# return 0 if str is an integer
function bes_str_is_integer()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_str_is_integer str"
    return 1
  fi
  local _str="${1}"
  local _pattern='^[0-9]+$'
  if [[ ${_str} =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

# return 0 if str starts with head
function bes_str_starts_with()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_starts_with str head"
    return 1
  fi
  local _str="${1}"
  local _head="${2}"
  local _pattern="^${_head}.*$"
  if [[ "${_str}" =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

# return 0 if str ends with tail
function bes_str_ends_with()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_ends_with str tail"
    return 1
  fi
  local _str="${1}"
  local _tail="${2}"
  local _pattern="^.*${_tail}$"
  if [[ "${_str}" =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

# Remove head from str
function bes_str_remove_head()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_remove_head str head"
    return 1
  fi
  local _str="${1}"
  local _head="${2}"
  echo ${_str#${_head}}
  return 0
}

# Remove tail from str
function bes_str_remove_tail()
{
  if [[ $# != 2 ]]; then
    bes_message "usage: bes_str_remove_tail str tail"
    return 1
  fi
  local _str="${1}"
  local _tail="${2}"
  echo ${_str%${_tail}}
  return 0
}

# return 0 if str is an integer
function bes_str_is_integer()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_str_is_integer str"
    return 1
  fi
  local _str="${1}"
  local _pattern='^[0-9]+$'
  if [[ ${_str} =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

bes_log_trace_file path "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_log_trace_file system "begin"

# A basic UNIX path that is guranteed to find common exeutables on all platforms
_BES_BASIC_PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/sbin:/usr/bin:/bin:/c/Windows/System32

# An implemention of "which" with the same semantics as /usr/bin/which for cases
# where /usr/bin/which is not found
function _bes_which()
{
  function _bes_which_help()
  {
    echo "_bes_which: illegal option -- ${_key}"
    echo "usage: _bes_which [-as] program ..."
  }
  
  local _positional_args=()
  local _key
  local _list_all_instances=false
  local _no_output=false
  while [[ $# -gt 0 ]]; do
    _key="${1}"
    case ${_key} in
      -a)
        _list_all_instances=true
        shift # past argument
        ;;
      -s)
        _no_output=true
        shift # past argument
        ;;
      -*)
        _bes_which_help
        return 1
        ;;
      *)    # unknown option
        _positional_args+=("${1}") # save it in an array for later
        shift # past argument
        ;;
    esac
  done

  set -- "${_positional_args[@]}" # restore positional parameters
  
  if [[ $# < 1 ]]; then
    _bes_which_help
    return 1
  fi

  local _programs
  declare -a _programs
  _programs=( ${1+"$@"} )
  local _one_whiches
  declare -a _one_whiches
  local _one_rv
  local _found_all=true
  local _one_which

  for _program in "${_programs[@]}"; do
    _one_whiches=( $(_bes_which_one_program "${_program}" ${_list_all_instances}) )
    _one_rv=$?
    if [[ ${_one_rv} == 0 ]]; then
      if [[ ${_no_output} == "false" ]]; then
        for _one_which in "${_one_whiches[@]}"; do
          echo "${_one_which}"
        done
      fi
    else
      _found_all=false
    fi
  done

  if [[ ${_found_all} == "true" ]]; then
    return 0
  fi
  return 1
}

function _bes_which_one_program()
{
  if [[ $# != 2 ]]; then
    echo "Usage: _bes_which_one_program program list_all"
    return 1
  fi
  local _program="${1}"
  local _list_all=${2}
  local _path
  declare -a _path
  local _path_entry
  local _possible_which
  local _found_any=false

  if [[ -x "${_program}" ]]; then
    echo "${_program}"
    return 0
  fi
  
  IFS=':' read -ra _path <<< "${PATH}"
  for _path_entry in "${_path[@]}"; do
    _possible_which=${_path_entry}/${_program}
    if [[ -x "${_possible_which}" ]]; then
      echo "${_possible_which}"
      if [[ ${_list_all} != "true" ]]; then
        return 0
      fi
      _found_any=true
    fi
  done
  if [[ ${_found_any} == "true" ]]; then
    return 0
  fi
  return 1
}

# When found which is in the same place on both linux and macos
# when not found use the handrolled _bes_which instead
if [[ -x /usr/bin/which ]]; then
  _BES_WHICH_EXE=/usr/bin/which
else
  _BES_WHICH_EXE=_bes_which
fi
_BES_WHICH_EXE=_bes_which

# Use which to find the abs paths to a handful of executables used in this library.
# The reason for using _BES_BASIC_PATH in this manner is that we want this library to
# work *even* if the callers PATH is empty or "bad"
_BES_AWK_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} awk)
_BES_BASENAME_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} basename)
_BES_CAT_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} cat)
_BES_DIFF=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} diff)
_BES_DIRNAME_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} dirname)
_BES_EXPR=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} expr)
_BES_GREP_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} grep)
_BES_MKDIR_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} mkdir)
_BES_PWD_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} pwd)
_BES_SED=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} sed)
_BES_TR_EXE=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} tr)
_BES_UNAME=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} uname)
_BES_WC=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} wc)
_BES_LS=$(PATH=${_BES_BASIC_PATH} ${_BES_WHICH_EXE} ls)

function bes_has_program()
{
  local _program="$1"
  $(${_BES_WHICH_EXE} "${_program}" >& /dev/null)
  local _rv=$?
  return ${_rv}
}

function bes_find_program()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_find_program env_var_name prog_name1 [ prog_name1 ... prog_nameN ]"
    return 1
  fi
  local _env_var_name=${1}
  shift
  local _exe=$(bes_var_get ${_env_var_name})
  if [[ -n ${_exe} ]]; then
    if ! $(bes_has_program ${_exe}); then
      echo ""
      return 1
    fi
    echo "${_exe}"
    return 0  
  fi
  for _exe in "$@"; do
    if bes_has_program ${_exe}; then
      echo ${_exe}
      return 0
    fi
  done
  echo ""
  return 1
}

function bes_system_info()
{
  local _uname=$(${_BES_UNAME})
  local _system='unknown'
  local _arch=$(${_BES_UNAME} -m)
  local _distro=
  local _major=
  local _minor=
  local _path=
  local _version=
  case "${_uname}" in
    Darwin)
      _system='macos'
      _version=$(/usr/bin/sw_vers -productVersion)
      _major=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $1; }')
      _minor=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $2; }')
      _path=${_system}-${_major}/${_arch}
      ;;
	  Linux)
      _system='linux'
      _version=$(${_BES_CAT_EXE} /etc/os-release | ${_BES_GREP_EXE} VERSION_ID= | ${_BES_AWK_EXE} -F"=" '{ print $2; }' | ${_BES_AWK_EXE} -F"." '{ printf("%s.%s\n", $1, $2); }' | ${_BES_TR_EXE} -d '\"')
      _major=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $1; }')
      _minor=$(echo ${_version} | ${_BES_AWK_EXE} -F"." '{ print $2; }')
      _distro=$(${_BES_CAT_EXE} /etc/os-release | ${_BES_GREP_EXE} -e '^ID=' | ${_BES_AWK_EXE} -F"=" '{ print $2; }')
      _path=${_system}-${_distro}-${_major}/${_arch}
      ;;
    MINGW64_NT*) # git bash
      _system="windows"
      _distro="mingw64"
      ;;
    MSYS_NT*) # msys2
      _system="windows"
      _distro="msys2"
      ;;
	esac

  if [[ ${_system} == "windows" ]]; then
    local _powershell=/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
    local _version=$(${_powershell} [System.Environment]::OSVersion | ${_BES_GREP_EXE} Win32NT | ${_BES_AWK_EXE} '{ print $2; }')
    local _major=$(echo ${_version} | ${_BES_AWK_EXE} -F'.' '{ print $1 }')
    local _minor=$(echo ${_version} | ${_BES_AWK_EXE} -F'.' '{ print $2 }')
    _path=${_system}-${_major}/${_arch}
  fi
  echo ${_system}:${_distro}:${_major}:${_minor}:${_arch}:${_path}
  return 0
}

function bes_system()
{
  local _path=$(bes_system_info | ${_BES_AWK_EXE} -F":" '{ print $1 }')
  echo ${_path}
  return 0
}

function bes_system_path()
{
  local _path=$(bes_system_info | ${_BES_AWK_EXE} -F":" '{ print $6 }')
  echo ${_path}
  return 0
}

function _bes_windows_version()
{
  local _version=$(cmd /c ver | grep "Microsoft Windows \[Version" | tr '[' ' ' | tr ']' ' ' | awk '{ print $4; }')
  echo ${_version}
  return 0
}

bes_log_trace_file system "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Unit testing code mostly borrowed from:
#   https://unwiredcouch.com/2016/04/13/bash-unit-testing-101.html

bes_import "bes_system.bash"

# The total number of tests and the current test index
_BES_TESTS_NUM_TOTAL=0
_BES_TESTS_INDEX=0

# Print all the unit tests defined in this script environment (functions starting with test_)
function bes_testing_print_unit_tests()
{
  if [[ ${BES_UNIT_TEST_LIST} ]]; then
    echo "${BES_UNIT_TEST_LIST}"
    return 0
  fi
  local _result
  declare -a _result
  i=$(( 0 ))
  for unit_test in $(declare -f | ${_BES_GREP_EXE} -o "^test_[a-zA-Z_0-9]*"); do
    _result[$i]=$unit_test
    i=$(( $i + 1 ))
  done
  echo ${_result[*]}
  return 0
}

# Call a function and print the exit code
function bes_testing_call_function()
{
  local _function=${1}
  shift
  ${_function} ${1+"$@"}
  local _rv=$?
  echo ${_rv}
  return 0
}

function _bes_testing_exit_code_filename()
{
  local _exit_code_filename="/tmp/_bes_testing_exit_code_$$"
  echo "${_exit_code_filename}"
  return 0
}

function _bes_testing_exit_code_filename_clean()
{
  local _exit_code_filename="$(_bes_testing_exit_code_filename)"
  rm -f "${_exit_code_filename}"
  return 0
}

function _bes_testing_exit_code_set()
{
  local _exit_code_filename="$(_bes_testing_exit_code_filename)"
  echo $1 > "${_exit_code_filename}"
  return 0
}

function _bes_testing_exit_code_get()
{
  local _exit_code_filename="$(_bes_testing_exit_code_filename)"
  local _exit_code=0
  if [[ -f "${_exit_code_filename}" ]]; then
    _exit_code=$(cat "${_exit_code_filename}")
  fi
  echo ${_exit_code}
  return $(${_BES_EXPR} ${_exit_code})
}

# Run all the unit tests found in this script environment
function bes_testing_run_unit_tests()
{
  local _tests=$(bes_testing_print_unit_tests)
  local _test
  local _rv
  local _index=$(${_BES_EXPR} 0)
  local _num_total=$(${_BES_EXPR} $(echo ${_tests} | ${_BES_WC} -w))
  _BES_TESTS_NUM_TOTAL=${_num_total}
  for _test in $_tests; do
    _index=$(${_BES_EXPR} ${_index} + 1)
    _BES_TESTS_INDEX=${_index}
    ${_test}
  done
  local _exit_code="$(_bes_testing_exit_code_get)"
  _bes_testing_exit_code_filename_clean
  exit ${_exit_code}
}

# Run that an expression argument is true and print that
function bes_assert()
{
  function _bes_testing_make_counter()
  {
    local _num_total=${1}
    local _index=${2}
    local _num_digits=$(${_BES_EXPR} $(printf ${_num_total} | ${_BES_WC} -c))
    local _format="%${_num_digits}d"
    local _counter=$(printf "[${_format} of ${_format}]" ${_index} ${_num_total})
    echo "${_counter}"
    return 0
  }
  
  local _filename=$($_BES_BASENAME_EXE ${BASH_SOURCE[1]})
  local _line=${BASH_LINENO[0]}
  local _function=${FUNCNAME[1]}
  local _counter="$(_bes_testing_make_counter ${_BES_TESTS_NUM_TOTAL} ${_BES_TESTS_INDEX})"
  local _header_passed="${_filename} ${_counter} passed: ${_function}"
  local _header_failed="${_filename} ${_counter} FAILED: ${_function}"
  eval "${1}"
  if [[ $? -ne 0 ]]; then
    echo "${_header_failed}: ${_filename}:${_line}: ${1}"
    if [[ -n ${BES_UNIT_TEST_FAIL} ]]; then
        exit 1
    fi
    _bes_testing_exit_code_set 1
  else
    echo "${_header_passed}"
  fi
}

# Make a temp dir for testing
function bes_testing_make_temp_dir()
{
  if [[ $# < 1 ]]; then
    echo "Usage: bes_testing_make_temp_dir label"
    return 1
  fi
  local _label="${1}"
  local _pid=$$
  local _basename="${_label}_${_pid}"
  local _tmpdir="$(mktemp -d)/${_basename}"
  mkdir -p "${_tmpdir}"
  local _normalized_tmpdir="$(command cd -P "${_tmpdir}" > /dev/null && command pwd -P )"
  echo "${_normalized_tmpdir}"
  return 0
}

# Return 0 if the content of a file matches content
function bes_testing_check_file()
{
  if [[ $# != 2 ]]; then
    echo "Usage: bes_testing_check_file filename content"
    return 1
  fi
  local _filename="${1}"
  local _content="${2}"
  echo "${_content}" | "${_BES_DIFF}" "${_filename}" - >& /dev/null
  local _rv=$?
  if [[ ${_rv} != 0 ]]; then
    echo "${_content}" | "${_BES_DIFF}" "${_filename}" -
  fi
  return ${_rv}
}
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

bes_import "bes_string.bash"

_bes_trace_file "begin"

# Return 0 if version is a valid software version in the form $major.$minor.$revision
function bes_version_is_valid()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_version_is_valid version"
    return 1
  fi
  local _version="${1}"
  local _pattern='^[0-9]+\.[0-9]+\.[0-9]+$'
  if [[ ${_version} =~ ${_pattern} ]]; then
    return 0
  fi
  return 1
}

# Return 0 if part is one of "major" "minor" or "revision"
function bes_version_part_name_is_valid()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_version_part_name_is_valid part"
    return 1
  fi
  local _part="${1}"
  case ${_part} in
    major|minor|revision)
      return 0
      ;;
	  *)
      ;;
	esac
  return 1
}

# Return the index of the version part
function _bes_version_part_index()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: _bes_version_part_index <part>"
    return 1
  fi
  local _part=${1}

  if ! bes_version_part_name_is_valid ${_part}; then
    bes_message "bes_version_get_part: invalid part: ${_part}"
    return 1
  fi

  local _index
  case ${_part} in
    major)
      _index=0
      ;;
    minor)
      _index=1
      ;;
    revision)
      _index=2
      ;;
	esac
  echo ${_index}
  return 0
  }
  
# get a version part
function bes_version_get_part()
{
  if [[ $# < 2 ]]; then
    bes_message "usage: bes_version_get_part version part"
    return 1
  fi
  local _version="${1}"
  local _part="${2}"

  if ! bes_version_is_valid ${_version}; then
    bes_message "bes_version_get_part: invalid version: ${_version}"
    return 1
  fi
  
  if ! bes_version_part_name_is_valid ${_part}; then
    bes_message "bes_version_get_part: invalid part: ${_part}"
    return 1
  fi

  local _parts=( $(bes_str_split ${_version} .) )
  local _index=$(_bes_version_part_index ${_part})
  echo ${_parts[${_index}]}
  return 0
}

# Bump a version.  part is optional and should one of major minor or revision
function bes_version_bump()
{
  if [[ $# < 1 ]]; then
    bes_message "usage: bes_version_bump version <part>"
    return 1
  fi
  local _version="${1}"
  local _part=revision
  shift
  if [[ $# > 0 ]]; then
    _part=${1}
  fi

  if ! bes_version_is_valid ${_version}; then
    bes_message "bes_version_bump: invalid version: ${_version}"
    return 1
  fi
  
  if ! bes_version_part_name_is_valid ${_part}; then
    bes_message "bes_version_bump: invalid part: ${_part}"
    return 1
  fi

  local _parts=( $(bes_str_split ${_version} .) )
  local _index=$(_bes_version_part_index ${_part})
  local _old_part=${_parts[${_index}]}
  local _new_part=$(expr ${_old_part} + 1)
  _parts[${_index}]=${_new_part}
  echo ${_parts[*]} | tr ' ' '.'
  return 0
}

function bes_version_bump_prefixed()
{
  if [[ $# < 2 ]]; then
    echo "usage: bes_version_bump_prefixed tag prefix <part>"
    return 1
  fi
  local _tag="${1}"
  shift
  local _prefix="${1}"
  shift
  local _part=revision
  if [[ $# > 0 ]]; then
    _part=${1}
  fi

  if ! bes_str_starts_with ${_tag} ${_prefix}; then
    bes_message "tag ${_tag} does not start with ${_prefix}"
    return 1
  fi
  
  local _version=$(bes_str_remove_head ${_tag} ${_prefix})
  local _new_version=$(bes_version_bump ${_version} ${_part})
  echo ${_prefix}${_new_version}
  
  return 0
}

# compare p1 and p2 numbers and return "lt" "gt" or "eq"
function _bes_version_part_compare()
{
  if [[ $# != 2 ]]; then
    echo "usage: _bes_version_part_compare p1 p2"
    return 1
  fi
  local _p1=${1}
  local _p2=${2}

  if (( ${_p1} < ${_p2} )); then
    echo lt
    return 0
  fi

  if (( ${_p1} > ${_p2} )); then
    echo gt
    return 0
  fi
  echo eq
  return 0
}

# compare v1 to v2 and return "lt" "gt" or "eq"
function bes_version_compare()
{
  if [[ $# != 2 ]]; then
    echo "usage: bes_version_compare v1 v2"
    return 1
  fi
  local _v1="${1}"
  local _v2="${2}"

  if ! bes_version_is_valid ${_v1}; then
    bes_message "bes_version_compare: invalid v1: ${_v1}"
    return 1
  fi

  if ! bes_version_is_valid ${_v2}; then
    bes_message "bes_version_compare: invalid v2: ${_v2}"
    return 1
  fi

  local _v1_major=$(bes_version_get_part ${_v1} major)
  local _v1_minor=$(bes_version_get_part ${_v1} minor)
  local _v1_revision=$(bes_version_get_part ${_v1} revision)

  local _v2_major=$(bes_version_get_part ${_v2} major)
  local _v2_minor=$(bes_version_get_part ${_v2} minor)
  local _v2_revision=$(bes_version_get_part ${_v2} revision)

  local _cmp_major=$(_bes_version_part_compare ${_v1_major} ${_v2_major})
  if [[ ${_cmp_major} == lt ]]; then
    echo lt
    return 0
  fi
  if [[ ${_cmp_major} == gt ]]; then
    echo gt
    return 0
  fi

  local _cmp_minor=$(_bes_version_part_compare ${_v1_minor} ${_v2_minor})
  if [[ ${_cmp_minor} == lt ]]; then
    echo lt
    return 0
  fi
  if [[ ${_cmp_minor} == gt ]]; then
    echo gt
    return 0
  fi

  local _cmp_revision=$(_bes_version_part_compare ${_v1_revision} ${_v2_revision})
  if [[ ${_cmp_revision} == lt ]]; then
    echo lt
    return 0
  fi
  if [[ ${_cmp_revision} == gt ]]; then
    echo gt
    return 0
  fi
  echo eq
  return 0
}

_bes_trace_file "end"
#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

# Functions to do web requests stuff

_bes_trace_file "begin"

# Download a url to a file with optional username and password.
# uses curl or wget dependning on which one is found
function bes_web_request()
{
  if [[ $# < 1 ]]; then
    bes_message "Usage: bes_web_request url --data key=value --username username --password password --headers-file file"
    return 1
  fi
  local _url="${1}"
  shift
  local _username
  local _password
  local _datas=()
  local _headers=()
  local _headers_file=
  local _response_data_file=
  local _http_status_file=
  local _method=
  local _log_file=/dev/null
  local _enable_redirects=false
  local _positional_args=()
  local _key
  while [[ $# -gt 0 ]]; do
    _key="${1}"
    bes_debug_message "bes_web_request: checking key ${_key} ${2}"
    case ${_key} in
      --username)
        _username="${2}"
        shift # past argument
        shift # past value
        ;;
      --password)
        _password="${2}"
        shift # past argument
        shift # past value
        ;;
      --data)
        _datas+=( "${2}" )
        shift # past argument
        shift # past value
        ;;
      --header)
        _headers+=( "${2}" )
        shift # past argument
        shift # past value
        ;;
      --headers-file)
        _headers_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --response-data-file)
        _response_data_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --http-status-file)
        _http_status_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --method)
        _method="${2}"
        shift # past argument
        shift # past value
        ;;
      --log-file)
        _log_file="${2}"
        shift # past argument
        shift # past value
        ;;
      --enable-redirects)
        _enable_redirects=true
        shift # past argument
        ;;
      *)    # unknown option
        _positional_args+=("${1}") # save it in an array for later
        shift # past argument
        ;;
    esac
  done
  
  bes_debug_message "             _datas: ${_datas[@]}"
  bes_debug_message "           _headers: ${_headers[@]}"
  bes_debug_message "      _headers_file: ${_headers_file}"
  bes_debug_message "            _method: ${_method}"
  bes_debug_message "  _http_status_file: ${_http_status_file}"
  bes_debug_message "          _log_file: ${_log_file}"
  bes_debug_message "          _password: ${_password}"
  bes_debug_message "          _username: ${_username}"
  bes_debug_message "_response_data_file: ${_response_data_file}"
  bes_debug_message "  _enable_redirects: ${_enable_redirects}"
  
  set -- "${_positional_args[@]}" # restore positional parameters

  if [[ -n "${_username}" ]] && [[ -z "${_password}" ]]; then
    bes_message "bes_web_request: If username is given then password needs to be given too."
    return 1
  fi

  if [[ -n "${_password}" ]] && [[ -z "${_username}" ]]; then
    bes_message "bes_web_request: If password is given then username needs to be given too."
    return 1
  fi
  
  local _rv
  if $(bes_has_program curl); then
    local _curl_args=()
    if [[ -n "${_username}" ]]; then
      _curl_args+=( "--user" "${_username}:${_password}" )
    fi
    local _data
    for _data in "${_datas[@]}"; do
      _curl_args+=( "--data" "${_data}" )
    done
    local _header
    for _header in "${_headers[@]}"; do
      _curl_args+=( "--header" "${_header}" )
    done
    if [[ -n "${_headers_file}" ]]; then
      _curl_args+=( "--header" "@${_headers_file}" )
    fi
    if [[ -n "${_method}" ]]; then
      _curl_args+=( "--request" "${_method}" )
    fi
    if [[ ${_enable_redirects} == "true" ]]; then
      _curl_args+=( "--location" )
    fi
    _bes_web_request_curl "${_url}" "${_response_data_file}" "${_http_status_file}" "${_log_file}" "${_curl_args[@]}"
    _rv=$?
    return ${_rv}
  fi
  
  if $(bes_has_program wget); then
    local _wget_args=()
    if [[ -n "${_username}" ]]; then
      _wget_args+=( "--user" "${_username}" )
      _wget_args+=( "--password" "${_password}" )
    fi
    local _data
    for _data in "${_datas[@]}"; do
      _wget_args+=( "--post-data"="${_data}" )
    done
    local _header
    for _header in "${_headers[@]}"; do
      _wget_args+=( "--header"="${_header}" )
    done
    _bes_web_request_wget "${_url}" "${_response_data_file}" "${_http_status_file}" "${_log_file}" "${_wget_args[@]}"
    _rv=$?
    return ${_rv}
  fi

  bes_message "bes_web_request: no curl or wget found."
  
  return 1
}

function _bes_web_request_curl()
{
  if [[ $# < 4 ]]; then
    bes_message "Usage: _bes_web_request_curl url response_data_file http_status_file log_file <extra_args>"
    return 1
  fi
  local _url="${1}"
  shift
  local _response_data_file="${1}"
  shift
  local _http_status_file="${1}"
  shift
  local _log_file="${1}"
  shift
  local _extra_args=(${1+"$@"})
  local _http_status_args=""
  local _args=()

  _args+=( "--silent" )
  if [[ -n "${_http_status_file}" ]]; then
    _args+=( "--write-out" "%{http_code}\n" )
  fi
  if [[ -n "${_response_data_file}" ]]; then
    _args+=( "--output" "${_response_data_file}" )
  fi

  local _arg
  for _arg in "${_extra_args[@]}"; do
    _args+=( "${_arg}" )
  done
    
  _args+=( "${_url}" )
  bes_debug_message "_bes_web_request_curl: calling: curl ${_args[@]}"
  local _curl_output=$(curl ${_args[@]} 2> "${_log_file}")
  local _curl_exit_code=$?
  if [[ -n "${_http_status_file}" ]]; then
    echo ${_curl_output} > "${_http_status_file}"
  fi
  return ${_curl_exit_code}
}

function _bes_download_wget()
{
  if [[ $# < 4 ]]; then
    bes_message "Usage: _bes_download_wget url filename <username> <password>"
    return 1
  fi
  local _url="${1}"
  local _filename="${2}"
  local _username="${3}"
  local _password="${4}"
  local _auth_args
  if [[ -n "${_username}" && -n "${_password}" ]]; then
    _auth_args="--user ${_username} --password ${_password}"
  else
    _auth_args=""
  fi

  # FIXME: need more error checking here
  wget --quiet --user ${_auth_args} ${_url} -O ${_filename}
  if [[ -f ${_filename} ]]; then
    return 0
  fi
  return 1
}

_bes_trace_file "end"
