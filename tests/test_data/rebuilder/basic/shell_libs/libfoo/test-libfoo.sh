#!/bin/bash

set -e -x

output=$(libfoo.py one two tre)
test "$output" == 'libfoo: one two tre'
