#!/bin/bash

set -e

function main()
{
  local _this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  local _root_dir="$(cd "${_this_dir}/.." && pwd)"

  "${_root_dir}/r" "${_root_dir}/bin/bes_app.py" ${1+"$@"}

  return 0
}

main ${1+"$@"}
