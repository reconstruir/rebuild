#!/bin/bash

set -e -x

output=$(foo.py one two tre)
test "$output" == 'foo: one two tre'
