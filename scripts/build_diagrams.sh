#!/bin/bash

set -e

function main()
{
  source $(_build_diagrams_this_dir)/../bes_bash/bes_bash.bash

  local _this_dir="$(_build_diagrams_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _best="${_root_dir}/bin/best.py"
  local _best_script="${_root_dir}/bin/best.py"
  local _diagrams="${_root_dir}/best.exe"

  make -C ${_root_dir}/lib/bes/config/ini clean all
  make -C ${_root_dir}/tests/lib/bes/btl clean all
  
  return 0
}

function _build_diagrams_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
