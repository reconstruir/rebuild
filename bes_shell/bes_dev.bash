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
      --set-python-path)
        _set_python_path=true
        shift # past argument
        ;;
      --change-dir)
        _change_dir=true
        shift # past argument
        ;;
      --no-change-dir|-ncd)
        _change_dir=false
        shift # past argument
        ;;
      --set-title)
        _set_title=true
        shift # past argument
        ;;
      --no-set-title|-nst)
        _set_title=false
        shift # past argument
        ;;
      --light|-l)
        _set_path=true
        _set_python_path=true
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
  if [[ ${_set_python_path} == true ]]; then
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
