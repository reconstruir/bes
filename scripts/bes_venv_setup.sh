#!/bin/bash

set -e

function main()
{
  source $(_this_dir_bes_venv_setup)/../bes_shell/bes_all.bash

  local _this_dir="$(_this_dir_bes_venv_setup)"
  local _root_dir="$(bes_abs_path ${_this_dir}/..)"
  local _best="${_root_dir}/bin/best.py"

  local _projects_root_dir="${_root_dir}/VE"
  local _requirements="${_root_dir}/requirements.txt"
  local _requirements_test="${_root_dir}/requirements-test.txt"
  
  ${_best} pip_project install_requirements --root-dir "${_projects_root_dir}" bes_venv "${_requirements}"
  ${_best} pip_project install_requirements --root-dir "${_projects_root_dir}" bes_venv "${_requirements_test}"
  
  return 0
}

function _this_dir_bes_venv_setup()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
