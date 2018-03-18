#!/bin/bash

set -e -x

output=$(tbar.py one two tre)
test "$output" == 'tfoo: a b c # tbar: one two tre'
