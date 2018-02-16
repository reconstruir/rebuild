#!/bin/bash

diff=/Applications/TextWrangler.app/Contents/Helpers/twdiff
diff='diff -r'
$diff $(./experiments/pkg-config-test.sh ~/x/files/bin/pkg-config bin/rebuild_pkg_config.py)

