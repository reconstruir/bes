#!/bin/bash

_current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
_lib_dir="${_current_dir}/lib"
VIRTUAL_ENV="${_current_dir}/.venv" PYTHONPATH=${_lib_dir} uv run --no-project ${1+"$@"}
