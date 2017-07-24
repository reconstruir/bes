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
    printf "\nUsage: bes-setup root_dir module_dir\n\n"
    return 1
  fi
  local _root_dir=$1
  local _module_dir=$2
  export PATH=${_root_dir}/bin:${PATH}
  export PYTHONPATH=${_root_dir}/${_module_dir}:${PYTHONPATH}
  return 0
}
