#!/bin/bash

set -e -x

output=$(tbar.py one two tre)
test "$output" == 'tbar: one two tre'
