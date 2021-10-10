#!/bin/bash

set -e

function main()
{
  local _this_dir="$(_best_sh_this_dir)"
  source "${_this_dir}/../bes_bash/bes_bash.bash"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _python_lib_dir="$(bes_path_abs_dir ${_this_dir}/../lib)"

  export PYTHONPATH="${_python_lib_dir}:${PYTHONPATH}"
  exec ${_root_dir}/bin/best.py ${1+"$@"}

  return 0
}

function _best_sh_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
