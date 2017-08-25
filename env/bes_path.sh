_bes_path_root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

function bes_path_append()
{
  if [ $# -lt 2 ]; then
    echo "usage: bes_path_append path part1 part2 ... parnN"
    return 1
  fi
  $(_bes_path_root)/bin/bes_path.py append "$@"
  return $?
}

function bes_path_prepend()
{
  if [ $# -lt 2 ]; then
    echo "usage: bes_path_prepend path part1 part2 ... parnN"
    return 1
  fi
  $(_bes_path_root)/bin/bes_path.py prepend "$@"
  return $?
}

function bes_path_cleanup()
{
  if [ $# -lt 1 ]; then
    echo "usage: bes_path_cleanup path"
    return 1
  fi
  $(_bes_path_root)/bin/bes_path.py cleanup "$@"
  return $?
}

function bes_path_print()
{
  if [ $# -lt 1 ]; then
    echo "usage: bes_path_print path"
    return 1
  fi
  $(_bes_path_root)/bin/bes_path.py print -l "$@"
  return $?
}

function bes_env_path_cleanup()
{
  local _var_name="$1"
  local _result=$(_bes_path_root)/bin/bes_path.py cleanup $_var_name)
  echo $_result
  return 0
}
