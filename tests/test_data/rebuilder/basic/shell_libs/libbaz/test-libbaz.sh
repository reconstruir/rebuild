#!/bin/bash

set -e -x

output=$(libbaz.py one two tre)
test "$output" == 'libbaz: one two tre'
