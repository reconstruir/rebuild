#!/bin/bash

_bes_root_dir=$(cd ../bes && pwd)
_bat_root_dir=$(cd ../bat && pwd)
_bnet_root_dir=$(cd ../bnet && pwd)
PYTHONPATH=${_bes_root_dir}/lib:${_bat_root_dir}/lib:${_bnet_root_dir}/lib:$(pwd)/lib uv run ${1+"$@"}
