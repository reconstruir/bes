if [ -n "$_BES_TRACE" ]; then echo "bes_setup.sh begin"; fi

_bes_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

source "$(_bes_dev_root)/bes_shell/bes_shell.bash"

bes_dev()
{
  local _root_dir=$(_bes_dev_root)
  bes_setup "${_root_dir}" ${1+"$@"}
  source "${_root_dir}/env/bes_venv_activate.bash"
  return 0
}

bes_undev()
{
  local _root_dir=$(_bes_dev_root)
  bes_unsetup ${_root_dir}
  return 0
}

if [ -n "$_BES_TRACE" ]; then echo "bes_setup.sh end"; fi
