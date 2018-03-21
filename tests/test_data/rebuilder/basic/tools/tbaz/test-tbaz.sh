#!/bin/bash

set -e -x

output=$(tbaz.py one two tre)
test "$output" == 'tbaz: one two tre'
