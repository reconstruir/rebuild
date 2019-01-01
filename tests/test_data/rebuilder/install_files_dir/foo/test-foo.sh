#!/bin/bash

set -e -x

output=$(foo1.py one two tre)
test "$output" == 'foo1: one two tre'

output=$(foo2.py one two tre)
test "$output" == 'foo2: one two tre'
