#!/bin/bash

set -e

function main()
{
  source $(_bes_venv_setup_this_dir)/../bes_bash/bes_bash.bash
  local _this_dir="$(_bes_venv_setup_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _best="${_root_dir}/bin/best.py"
  local _python_version=$(cat "${_root_dir}/env/python.version")
  local _python_exe="$(which python${_python_version})"
  if [ -z "${_python_exe}" ]; then
    _python_exe="$(bes_python_find_default)"
  fi
  _python_version=$(bes_python_exe_version "${_python_exe}")
  
  ${_python_exe} ${_best} pip_project install_requirements \
             --root-dir "${_root_dir}/VE/bes" \
             --python-version ${_python_version} \
             $@
  return 0
}

function _bes_venv_setup_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
