#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

_bes_trace_file "begin"

# Read a value from a config file
function bes_config_get()
{
  if [[ $# != 3 ]]; then
    echo "usage: bes_config_get filename section key"
    return 1
  fi
  local _filename="${1}"
  local _section="${2}"
  local _key="${3}"

  bes_file_check "${_filename}" 

  local __section_line_number
  local __line_number
  local __value
  if _bes_config_find_entry "${_filename}" ${_section} ${_key} __section_line_number __line_number __value; then
    echo "${__value}"
    return 0
  fi
  echo ""
  return 1
}

# Read a value from a config file
function bes_config_set()
{
  if [[ $# != 4 ]]; then
    echo "usage: bes_config_set filename section key value"
    return 1
  fi
  local _filename="${1}"
  local _section="${2}"
  local _key="${3}"
  local _value="${4}"

  bes_file_check "${_filename}" 

  if ! bes_config_has_section "${_filename}" "${_section}"; then
    _bes_config_add_section "${_filename}" "${_section}"
  fi
  local __section_line_number
  local __line_number
  local __value
  if _bes_config_find_entry "${_filename}" ${_section} ${_key} __section_line_number __line_number __value; then
    echo "${__value}"
    return 0
  fi
  echo ""
  return 0
}

function _bes_config_find_entry()
{
  if [[ $# != 6 ]]; then
    echo "usage: _bes_config_find_key filename section key section_line_number_result_var line_number_result_var value_result_var"
    return 1
  fi
  local _filename="${1}"
  local _section="${2}"
  local _key="${3}"
  local _section_line_number_result_var=${5}
  local _line_number_result_var=${5}
  local _value_result_var=${6}

  local _found_entry=false
  local _found_value
  local _found_line_number
  local _state=state_expecting_section
  local _next_key
  local _next_value
  local _next_token_type
  local _next_line_number
  
  local _tokens=( $(_bes_config_tokenize "${_filename}") )
  local _token
  local _parts
  declare -a _parts
  
  for _token in ${_tokens[@]}; do
    _parts=( $(echo ${_token} | tr ':' ' ') )
    _next_token_type=${_parts[0]}
    _next_line_number=${_parts[1]}
    _next_text=${_parts[2]}
    _next_key=${_parts[3]}
    _next_value=${_parts[4]}

    case ${_state} in
      state_expecting_section)
        case ${_next_token_type} in
          token_section)
            if [[ "${_next_text}" == "${_section}" ]]; then
              _state=state_wanted_section
            else
              _state=state_ignore_section
            fi
            ;;
          token_comment)
            ;;
          token_entry)
            true
            ;;
          token_whitespace)
            ;;
        esac
        ;;
      state_ignore_section)
        case ${_next_token_type} in
          token_section)
            if [[ "${_next_text}" == "${_section}" ]]; then
              _state=state_wanted_section
            else
              _state=state_ignore_section
            fi
            ;;
          token_comment|entry|whitespace)
            ;;
        esac
        ;;
      state_wanted_section)
        case ${_next_token_type} in
          token_section)
            _state=state_done
            ;;
          token_comment|token_whitespace)
            ;;
          token_entry)
            if [[ "${_next_key}" == "${_key}" ]]; then
              _found_value=${_next_value}
              _found_line_number=${_next_line_number}
              _found_entry=true
            fi
            ;;
        esac
        ;;
      state_done)
        break
        ;;
    esac
    
  done
  
  if ${_found_entry}; then
    eval "${_line_number_result_var}='${_found_line_number}'"
    eval "${_value_result_var}='${_found_value}'"
    return 0
  fi
  return 1
}

# ' ' @SPACE@
# ':' @COLON@
function _bes_config_text_escape()
{
  local _text="${1}"
  local _patterns=( "s/@SPACE@/%%SPACE%%/g" "s/@COLON@/%%COLON%%/g" "s/ /@SPACE@/g" "s/:/@COLON@/g" )
  local _pattern
  local _tmp_command_file=/tmp/tmp__bes_config_text_unescape_command_file_$$
  rm -f "${_tmp_command_file}"
  for _pattern in "${_patterns[@]}"; do
    echo "${_pattern}" >> "${_tmp_command_file}"
  done
  echo "${_text}" | sed -f "${_tmp_command_file}"
  rm -f "${_tmp_command_file}"
  return 0
}

# undo the action of _bes_config_text_escape
function _bes_config_text_unescape()
{
  local _text="${1}"
  local _patterns=( "s/%%SPACE%%/@SPACE@/g" "s/%%COLON%%/@COLON@/g" "s/@SPACE@/ /g" "s/@COLON@/:/g" )
  local _pattern
  local _tmp_command_file=/tmp/tmp__bes_config_text_unescape_command_file_$$
  rm -f "${_tmp_command_file}"
  for _pattern in "${_patterns[@]}"; do
    echo "${_pattern}" >> "${_tmp_command_file}"
  done
  echo "${_text}" | sed -f "${_tmp_command_file}"
  rm -f "${_tmp_command_file}"
  return 0
}

function _bes_config_parse_section_name()
{
  local _text="${1}"
  if [[ "${_text}" =~ \[(.+)\] ]]; then
    local _section_name="${BASH_REMATCH[1]}"
    if [[ -z "${_section_name}" ]]; then
      return 1
    fi
    echo ${BASH_REMATCH[1]}
    return 0
  fi
  return 1
}

function _bes_config_parse_entry()
{
  local _text="${1}"

  local _key="$(bes_string_partition "${_text}" ":" | head -1)"
  local _delim="$(bes_string_partition "${_text}" ":" | tail -2 | head -1)"
  local _value="$(bes_string_partition "${_text}" ":" | tail -1)"

#  echo _text ${_text} > $(tty)
#  echo _key ${_key} > $(tty)
#  echo _delim ${_delim} > $(tty)
#  echo _value ${_value} > $(tty)
  
  if [[ ${_delim} != ":" ]]; then
    return 1
  fi

  local _stripped_key=$(bes_string_strip "${_key}")
  local _stripped_value=$(bes_string_strip "${_value}")
  local _escaped_key=$(_bes_config_text_escape "${_stripped_key}")
  local _escaped_value=$(_bes_config_text_escape "${_stripped_value}")
  echo ${_escaped_key}:${_escaped_value}
  return 0
}

# Tokenize a config file and produce tokens as such
# ${token_type}:${line_number}:${text}:${key}:${value}
function _bes_config_tokenize()
{
  if [[ $# != 1 ]]; then
    echo "usage: _bes_config_tokenize filename"
    return 1
  fi
  local _filename="${1}"
  local _line_number=1
  local _line
  local _token_type
  local _text
  local _rest
  while IFS= read -r _line; do
    _token_type=$(_bes_config_token_type "${_line}")
    case ${_token_type} in
      token_section)
        _text="$(_bes_config_parse_section_name "${_line}")"
        _rest=":"
        ;;
      token_comment)
        _text="$(bes_string_strip "${_line}")"
        _rest=":"
        ;;
      token_entry)
        _text=$(_bes_config_text_escape "${_line}")
        _rest=$(_bes_config_parse_entry "${_line}")
        ;;
      token_whitespace)
        _text=""
        _rest=":"
        ;;
    esac
    echo ${_token_type}:${_line_number}:${_text}:${_rest}
    _line_number=$(( _line_number + 1 ))
  done < "${_filename}"
  return 0
}

function _bes_config_token_type()
{
  local _line="${1}"

  if [[ $(echo "${_line}" | cut -b 1) == '[' ]]; then
    echo "token_section"
    return 0
  fi

  local _stripped_line="$(bes_string_strip "${_line}")"
  if [[ -z "${_stripped_line}" ]]; then
    echo "token_whitespace"
    return 0
  fi
  if [[ $(echo "${_stripped_line}" | cut -b 1) == '#' ]]; then
    echo "token_comment"
    return 0
  fi
  echo "token_entry"
  return 0
}

function bes_config_has_section()
{
  if [[ $# != 2 ]]; then
    echo "usage: _bes_config_has_section filename section"
    return 1
  fi

  local _filename="${1}"
  local _section="${2}"
  local _tokens=( $(_bes_config_tokenize "${_filename}") )
  local _token
  local _parts
  declare -a _parts
  
  for _token in ${_tokens[@]}; do
    _parts=( $(echo ${_token} | tr ':' ' ') )
    _next_token_type=${_parts[0]}
    _next_line_number=${_parts[1]}
    _next_text=${_parts[2]}
    _next_key=${_parts[3]}
    _next_value=${_parts[4]}

    if [[ ${_next_token_type} == "token_section" ]]; then
      if [[ "${_next_text}" == "${_section}" ]]; then
        return 0
      fi
    fi
  done
  return 1
}

function _bes_config_add_section()
{
  if [[ $# != 2 ]]; then
    echo "usage: _bes_config_has_section filename section"
    return 1
  fi

  local _filename="${1}"
  local _section="${2}"

  printf "\n[%s]\n\n" "${_section}" >> "${_filename}"
  return 0
}

function _bes_config_add_entry()
{
  if [[ $# != 4 ]]; then
    echo "usage: _bes_config_has_section filename section key value"
    return 1
  fi

  local _filename="${1}"
  local _section="${2}"
  local _key="${3}"
  local _value="${4}"

  printf "\n[%s]\n\n" "${_section}" >> "${_filename}"
  return 0
}

_bes_trace_file "end"
