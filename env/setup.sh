_bes_dev_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

_BES_DEV_ROOT=$(_bes_dev_root)

source $_BES_DEV_ROOT/env/bes_framework.sh

bes-go()
{
  cd $_BES_DEV_ROOT
  return 0
}

bes-dev-setup()
{
  bes-setup $_BES_DEV_ROOT ${1+"$@"}
  return 0
}
