#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

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
