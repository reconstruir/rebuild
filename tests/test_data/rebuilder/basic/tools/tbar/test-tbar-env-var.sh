#!/bin/bash

set -e -x

output="$TBAR_ENV1 $TBAR_ENV2"
test "$output" == 'foo bar'
