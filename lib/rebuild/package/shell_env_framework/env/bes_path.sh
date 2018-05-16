
if [ -n "$_BES_TRACE" ]; then echo "bes_path.sh begin"; fi

function bes_path_append()
{
  if [ $# -lt 2 ]; then
    echo "usage: bes_path_append path part1 part2 ... parnN"
    return 1
  fi
  $_BES_DEV_ROOT/bin/bes_path.py append "$@"
  return $?
}

function bes_path_prepend()
{
  if [ $# -lt 2 ]; then
    echo "usage: bes_path_prepend path part1 part2 ... parnN"
    return 1
  fi
  $_BES_DEV_ROOT/bin/bes_path.py prepend "$@"
  return $?
}

function bes_path_remove()
{
  if [ $# -lt 2 ]; then
    echo "usage: bes_path_remove path part1 part2 ... parnN"
    return 1
  fi
  $_BES_DEV_ROOT/bin/bes_path.py remove "$@"
  return $?
}

function bes_path_cleanup()
{
  if [ $# -lt 1 ]; then
    echo "usage: bes_path_cleanup path"
    return 1
  fi
  $_BES_DEV_ROOT/bin/bes_path.py cleanup "$@"
  return $?
}

function bes_path_print()
{
  if [ $# -lt 1 ]; then
    echo "usage: bes_path_print path"
    return 1
  fi
  $_BES_DEV_ROOT/bin/bes_path.py print -l "$@"
  return $?
}

function bes_env_path_cleanup()
{
  local _var_name="$1"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_cleanup "$_value")
  bes_var_set $_var_name "$_new_value"
  return 0
}

function bes_env_path_append()
{
  local _var_name="$1"
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_append "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_prepend()
{
  local _var_name="$1"
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_prepend "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_remove()
{
  local _var_name="$1"
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_remove "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_clear()
{
  local _var_name="$1"
  bes_var_set $_var_name ""
  export $_var_name
  return 0
}

if [ -n "$_BES_TRACE" ]; then echo "bes_path.sh end"; fi
