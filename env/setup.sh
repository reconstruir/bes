if [ -n "$_BES_TRACE" ]; then echo "bes_setup.sh begin"; fi

_bes_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

_BES_DEV_ROOT=$(_bes_dev_root)

source ${_BES_DEV_ROOT}/bes_shell/bash/bes_shell/bes_shell.sh

bes_dev()
{
  bes_setup ${_BES_DEV_ROOT} ${1+"$@"}
  return 0
}

bes_undev()
{
  bes_unsetup ${_BES_DEV_ROOT}
  return 0
}

if [ -n "$_BES_TRACE" ]; then echo "bes_setup.sh end"; fi
