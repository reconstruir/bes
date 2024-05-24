if [ -n "$_BES_TRACE" ]; then echo "bes_setup.sh begin"; fi

_bes_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

bes_dev()
{
  local _bes_root_dir="$(_bes_dev_root)"
  source "$(_bes_dev_root)/bes_bash/bes_bash.bash"
  local _virtual_env_setup="${_bes_root_dir}/env/bes_venv_activate.bash"
  local _python_version=$(cat "${_bes_root_dir}/env/python.version")
  bes_dev_setup "${_bes_root_dir}" \
                --set-path \
                --set-python-path \
                --set-title \
                --venv-config "${_virtual_env_setup}" \
                --venv-activate \
                --change-dir \
                ${1+"$@"}
  bes_env_path_prepend PYTHONPATH "${_bes_root_dir}/VE/bes/lib/python${_python_version}/site-packages"
  return $?
}

bes_undev()
{
  local _bes_root_dir="$(_bes_dev_root)"
  source "$(_bes_dev_root)/bes_bash/bes_bash.bash"
  bes_dev_unsetup "${_bes_root_dir}"
  return 0
}

if [ -n "$_BES_TRACE" ]; then echo "bes_setup.sh end"; fi
