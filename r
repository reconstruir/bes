#!/bin/bash

_current_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
_lib_dir="${_current_dir}/lib"
PYTHONPATH=${_lib_dir} uv run --no-project ${1+"$@"}
