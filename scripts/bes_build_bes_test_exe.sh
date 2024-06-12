#!/bin/bash

set -e

function main()
{
  source $(_bes_build_bes_test_exe_this_dir)/../bes_bash/bes_bash.bash

  local _this_dir="$(_bes_build_bes_test_exe_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _best="${_root_dir}/bin/best.py"
  local _best_script="${_root_dir}/bin/bes_test.py"
  local _bes_test_exe="${_root_dir}/bes_test.exe"
  local _python_version=$(cat "${_root_dir}/env/python.version")

  ${_best} pyinstaller build \
           --build-dir _BES_TEST_BUILD \
           --clean \
           --log-level info \
           --python-version ${_python_version} \
           "${_best_script}" \
           "${_bes_test_exe}"
  
  return 0
}

function _bes_build_bes_test_exe_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
