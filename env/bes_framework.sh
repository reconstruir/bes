
#source $_BES_DEV_ROOT/env/bes_path.sh

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
  bes_path_dedup PATH

  export PYTHONPATH=${_root_dir}:${PYTHONPATH}
  bes_path_dedup PYTHONPATH

  if [ $_chdir -eq 1 ]; then
    cd $_root_dir
  fi
  
  return 0
}

# https://unix.stackexchange.com/questions/40749/remove-duplicate-path-entries-with-awk-command
bes_path_remove_dups()
{
  local _var_name="$1"
  local _result="$(printf %s $_var_name | awk -v RS=: -v ORS=: '!arr[$0]++')"
  echo $_result
  return 0
}

bes_path_remove_trailing_colon()
{
  local _var_name="$1"
  local _result=$(printf %s "$_var_name" | awk -v RS=: '{ if (!arr[$0]++) {printf("%s%s",!ln++?"":":",$0)}}')
  echo $_result
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

bes_path_dedup()
{
  local _var_name="$1"
  local _value=$(bes_var_get $_var_name)
  bes_var_set $_var_name $(bes_path_remove_dups "$_value")
  return 0
}

bes_path_cleanup()
{
  local _var_name="$1"
  local _value=$(bes_var_get $_var_name)
  _value=$(bes_path_remove_dups "$_value")
  _value=$(bes_path_remove_trailing_colon "$_value")
  bes_var_set $_var_name "$_value"
  return 0
}

