#!/bin/bash

_current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
_bes_root_dir="$(cd "${_current_dir}/../bes" && pwd)"
_bat_root_dir="$(cd "${_current_dir}/../bat" && pwd)"
_bnet_root_dir="$(cd "${_current_dir}/../bnet" && pwd)"

VIRTUAL_ENV="${_current_dir}/.venv" PYTHONPATH="${_bes_root_dir}/lib:${_bat_root_dir}/lib:${_bnet_root_dir}/lib:${_current_dir}/lib" uv run --no-project ${1+"$@"}
