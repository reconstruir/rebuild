#!/bin/bash

set -e -x

output=$(tfoo.py one two tre)
test "$output" == 'one two tre'
