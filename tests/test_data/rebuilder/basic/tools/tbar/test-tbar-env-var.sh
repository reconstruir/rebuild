#!/bin/bash

set -e -x

output="$TBAR_ENV1 $TBAR_ENV2 $TFOO_ENV1 $TFOO_ENV2"
test "$output" == 'foo bar tfoo_env1 tfoo_env2'
