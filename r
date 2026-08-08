#!/bin/bash

_current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# uv run picks which .venv to use based on the current working directory,
# not $VIRTUAL_ENV -- so this must cd here first to behave the same
# regardless of the caller's cwd (see
# ~/proj/bat/claude-docs/uv-dependencies.md §2).
cd "${_current_dir}"
uv run ${1+"$@"}
