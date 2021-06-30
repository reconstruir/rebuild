#-*- coding:utf-8; mode:shell-script; indent-tabs-mode: nil; sh-basic-offset: 2; tab-width: 2 -*-

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
