
# Source a shell file if it exists
bes-source()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes-source filename\n\n"
    return 1
  fi
  local _filename=$1
  if [ -f $_filename ]; then
     source $_filename
     return 0
  fi
  return 1
}

bes-invoke()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes-invoke function\n\n"
    return 1
  fi
  local _function=$1
  local _rv=1
  if type $_function >& /dev/null; then
    eval $_function
    _rv=$?
  fi
  return $_rv
}

bes-setup()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes-setup root_dir\n\n"
    return 1
  fi
  local _root_dir=$1
  local _chdir=0
  if [ $# -gt 1 ]; then
    _chdir=1
  fi
  
  export PATH=${_root_dir}/bin:${PATH}
  export PYTHONPATH=${_root_dir}:${PYTHONPATH}

  if [ $_chdir -eq 1 ]; then
    cd $_root_dir
  fi
  
  return 0
}
