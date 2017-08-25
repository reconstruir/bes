
if [ -n "$_BES_TRACE" ]; then echo "bes_framework.sh begin"; fi

source $_BES_DEV_ROOT/env/bes_path.sh

# Source a shell file if it exists
bes_source()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes_source filename\n\n"
    return 1
  fi
  local _filename=$1
  if [ -f $_filename ]; then
     source $_filename
     return 0
  fi
  return 1
}

bes_invoke()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes_invoke function\n\n"
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

bes_setup()
{
  if [ $# -lt 1 ]; then
    printf "\nUsage: bes_setup root_dir\n\n"
    return 1
  fi
  local _root_dir=$1
  local _chdir=0
  if [ $# -gt 1 ]; then
    _chdir=1
  fi

  bes_env_path_prepend PATH ${_root_dir}/bin
  bes_env_path_prepend PYTHONPATH ${_root_dir}

  if [ $_chdir -eq 1 ]; then
    cd $_root_dir
  fi
  
  return 0
}

# Get a var value
bes_var_get()
{
  eval 'printf "%s\n" "${'"$1"'}"'
}

# Set a var value
bes_var_set()
{
  eval "$1=\"\$2\""
}

if [ -n "$_BES_TRACE" ]; then echo "bes_framework.sh end"; fi
