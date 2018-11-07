
if [ -n "$_BES_TRACE" ]; then echo "bes_framework.sh begin"; fi

source $_BES_DEV_ROOT/env/bes_path.sh

# Return system host name.  linux or macos same is bes/system/host.py
_bes_host()
{
  local _name=$(uname -s)
  local _host='unknown'
  case $_name in
    Linux)
      _host='linux'
      ;;
    Darwin)
      _host='macos'
      ;;
  esac
  echo $_host
  if [ $_host = 'unknown' ]; then
     return 1
  fi
  return 0
}

# Source a shell file if it exists
function bes_source()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes_source filename\n\n"
    return 1
  fi
  local _filename=$1
  if [ -f $_filename ]; then
     source $_filename
     return 0
  fi
  return 1
}

bes_invoke()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes_invoke function\n\n"
    return 1
  fi
  local _function=$1
  local _rv=1
  if type $_function >& /dev/null; then
    eval $_function
    _rv=$?
  fi
  return $_rv
}

function bes_setup()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes_setup root_dir\n\n"
    return 1
  fi
  local _root_dir=$1
  local _dont_chdir=0
  if [ $# -gt 1 ]; then
    _dont_chdir=1
  fi

  bes_env_path_prepend PATH ${_root_dir}/bin
  bes_env_path_prepend PYTHONPATH ${_root_dir}/lib

  if [ $_dont_chdir -eq 0 ]; then
    cd $_root_dir
    bes_tab_title $(basename $_root_dir)
  fi
  
  return 0
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

function bes_PATH_cleanup()
{
  bes_env_path_cleanup PATH
}

function bes_PATH_prepend()
{
  bes_env_path_prepend PATH "$@"
}

function bes_PATH_append()
{
  bes_env_path_append PATH "$@"
}

function bes_PATH_remove()
{
  bes_env_path_remove PATH "$@"
}

function bes_PATH_append_cwd()
{
  bes_PATH_append $(pwd)
}

function bes_PATH_prepend_cwd()
{
  bes_PATH_prepend $(pwd)
}

function bes_PATH()
{
  bes_path_print "$PATH"
}

function bes_PYTHONPATH_prepend()
{
  bes_env_path_prepend PYTHONPATH "$@"
}

function bes_PYTHONPATH_append()
{
  bes_env_path_append PYTHONPATH "$@"
}

function bes_PYTHONPATH_remove()
{
  bes_env_path_remove PYTHONPATH "$@"
}

function bes_PYTHONPATH_append_cwd()
{
  bes_PYTHONPATH_append $(pwd)
}

function bes_PYTHONPATH_prepend_cwd()
{
  bes_PYTHONPATH_prepend $(pwd)
}

function bes_PYTHONPATH()
{
  bes_path_print $PYTHONPATH
}

function LD_LIBRARY_PATH_var_name()
{
  local _host=$(_bes_host)
  local _rv=
  case "$_host" in
    macos)
      _rv=DYLD_LIBRARY_PATH
      ;;
    linux|*)
      _rv=LD_LIBRARY_PATH
      ;;
  esac
  echo $_rv
  return 0
}

function bes_LD_LIBRARY_PATH_prepend()
{
  bes_env_path_prepend $(LD_LIBRARY_PATH_var_name) "$@"
}

function bes_LD_LIBRARY_PATH_append()
{
  bes_env_path_append $(LD_LIBRARY_PATH_var_name) "$@"
}

function bes_LD_LIBRARY_PATH_remove()
{
  bes_env_path_remove $(LD_LIBRARY_PATH_var_name) "$@"
}

function bes_LD_LIBRARY_PATH_append_cwd()
{
  bes_LD_LIBRARY_PATH_append $(pwd)
}

function bes_LD_LIBRARY_PATH_prepend_cwd()
{
  bes_LD_LIBRARY_PATH_prepend $(pwd)
}

function bes_LD_LIBRARY_PATH_clear()
{
  bes_env_path_clear $(LD_LIBRARY_PATH_var_name)
}

function bes_LD_LIBRARY_PATH()
{
  bes_path_print $(bes_var_get $(LD_LIBRARY_PATH_var_name))
}

function bes_MANPATH_prepend()
{
  bes_env_path_prepend MANPATH "$@"
}

function bes_MANPATH_append()
{
  bes_env_path_append MANPATH "$@"
}

function bes_MANPATH_remove()
{
  bes_env_path_remove MANPATH "$@"
}

function bes_MANPATH_append_cwd()
{
  bes_MANPATH_append $(pwd)
}

function bes_MANPATH_prepend_cwd()
{
  bes_MANPATH_prepend $(pwd)
}

function bes_MANPATH()
{
  bes_path_print $MANPATH
}

function bes_tab_title()
{
  echo -ne "\033]0;"$*"\007"
  local _prompt=$(echo -ne "\033]0;"$*"\007")
  export PROMPT_COMMAND='${_prompt}'
}

if [ -n "$_BES_TRACE" ]; then echo "bes_framework.sh end"; fi
