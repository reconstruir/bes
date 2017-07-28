bes-dev-root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

source $(bes-dev-root)/env/functions.sh

bes-go()
{
  cd $(bes-dev-root)
  return 0
}

bes-dev-setup()
{
  bes-setup $(bes-dev-root) ${1+"$@"}
  return 0
}
