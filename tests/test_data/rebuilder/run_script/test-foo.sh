#!/bin/bash

set -e -x

output=$(foo1.sh)
test "$output" == 'this the foo1'

output=$(foo2.sh)
test "$output" == 'this is foo2.'
