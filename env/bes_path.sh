function bes_path_append()
{
  if [ $# -lt 2 ]; then
    echo "usage: bes_path_append path part1 part2 ... parnN."
    return 1
  fi
  $BES_ROOT/bin/bes_path.py append "$@"
  return $?
}
