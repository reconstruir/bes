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

bes-dev()
{
  bes-setup $(bes-dev-root)
  bes-go
  return 0
}
