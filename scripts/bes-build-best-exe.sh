#!/bin/bash

set -e

function main()
{
  local _this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

  source ${_this_dir}/../bes_bash/bes_bash.bash

  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _bat_sh="${_root_dir}/../bat/bin/bat.sh"
  local _bes_script="${_root_dir}/bin/bes_app.py"
  local _best_output_exe="${_root_dir}/best.exe"
  local _python_version=$(cat "${_root_dir}/.python-version")

  ${_bat_sh} pyinstaller build \
           --build-dir _BES_TEST_BUILD \
           --clean \
           --log-level info \
           --hidden-import _cffi_backend \
           --onefile \
           --python-version ${_python_version} \
           "${_bes_script}" \
           "${_best_output_exe}"
  
  return 0
}

main ${1+"$@"}
