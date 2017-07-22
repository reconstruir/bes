bes-dev-root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

source $(bes-dev-root)/env/functions.sh

bes-dev()
{
  bes-setup $(bes-dev-root)
  return 0
}
