function _bes_venv_activate_main()
{
  source $(_bes_venv_activate_this_dir)/../bes_bash/bes_bash.bash

  local _this_dir="$(_bes_venv_activate_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _python="$(bes_python_find_default)"
  local _best="${_root_dir}/bin/best.py"

  local _projects_root_dir="${_root_dir}/VE/bes"
  local _requirements="${_root_dir}/requirements.txt"

  ${_this_dir}/bes_venv_setup.sh
  local _activate_script=$(${_python} ${_best} pip_project activate_script --root-dir "${_projects_root_dir}")
  echo ${_activate_script}
  
  return 0
}

function _bes_venv_activate_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

source $(_bes_venv_activate_main ${1+"$@"})
unset -f _bes_venv_activate_main
unset -f _bes_venv_activate_this_dir
