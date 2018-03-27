#!/bin/bash

set -e -x

output="$TFOO_ENV1 $TFOO_ENV2"
test "$output" == 'tfoo_env1 tfoo_env2'
