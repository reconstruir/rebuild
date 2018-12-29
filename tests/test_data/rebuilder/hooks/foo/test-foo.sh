#!/bin/bash

set -e -x

output=$(foo.py)
test "$output" == 'hook1 hook2'

