#!/bin/bash

_current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# --project tells uv which project's .venv/pyproject.toml to resolve
# against, without changing the invoked command's actual cwd (unlike a
# literal `cd` here would) -- so relative arguments you pass still
# resolve against wherever you actually are (see
# ~/proj/bat/claude-docs/uv-dependencies.md §2/§13).
uv run --project "${_current_dir}" ${1+"$@"}
