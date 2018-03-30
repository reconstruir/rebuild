#!/bin/bash

set -e -x

output="$TFOO_ENV1 $TFOO_ENV2"
test "$output" == 'foo_env1 foo_env2'
