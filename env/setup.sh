bes-root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

source $(bes-root)/env/functions.sh

bes-go()
{
  cd $(bes-root)
  return 0
}

bes-setup()
{
  bes-setup-dir $(bes-root)
  return 0
}
