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

bes_log_trace_file checksum "end"
