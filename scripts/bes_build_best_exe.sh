#!/bin/bash

set -e

function main()
{
  source $(_bes_build_best_exe_this_dir)/../bes_bash/bes_bash.bash

  local _this_dir="$(_bes_build_best_exe_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _best="${_root_dir}/bin/best.py"
  local _best_script="${_root_dir}/bin/best.py"
  local _best_exe="${_root_dir}/best.exe"

  ${_best} pyinstaller build \
           --build-dir _BES_TEST_BUILD \
           --clean \
           --log-level info \
           --python-version 3.8 \
           "${_best_script}" \
           "${_best_exe}"
  
  return 0
}

function _bes_build_best_exe_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
