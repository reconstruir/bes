# Source a sh file if it exists
bes-source()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes-source filename\n\n"
    return 1
  fi
  local filename=$1
  if [ -f $filename ]; then
     source $filename
     return 0
  fi
  return 1
}

bes-setup()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes-setup root\n\n"
    return 1
  fi
  local _root=$1
  export PATH=${_root}/bin:${PATH}
  export PYTHONPATH=${_root}/lib:${PYTHONPATH}
  return 0
}
