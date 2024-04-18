
function _bes_venv_activate_main()
{
  source $(_bes_venv_activate_this_dir)/../bes_bash/bes_bash.bash

  local _this_dir="$(_bes_venv_activate_this_dir)"
  local _root_dir="$(bes_path_abs_dir ${_this_dir}/..)"
  local _requirements=( "${_root_dir}/bes_requirements.txt" "${_root_dir}/bes_requirements_dev.txt" )
  local _system=$(bes_system)

  if bes_pip_project_requirements_are_stale "${_root_dir}/VE/bes" ${_requirements[@]}; then
    ${_this_dir}/bes_venv_setup.sh ${_requirements[@]}
  fi
  
  if [[ ${_system} == "windows" ]];
  then
    local _activate_script="${_root_dir}/VE/bes/Scripts/activate"
  else
    local _activate_script="${_root_dir}/VE/bes/bin/activate"
  fi
  echo "${_activate_script}"
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
