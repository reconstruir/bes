
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
  bes-path-dedup PATH

  export PYTHONPATH=${_root_dir}:${PYTHONPATH}
  bes-path-dedup PYTHONPATH

  if [ $_chdir -eq 1 ]; then
    cd $_root_dir
  fi
  
  return 0
}

# https://unix.stackexchange.com/questions/40749/remove-duplicate-path-entries-with-awk-command
bes-path-remove-dups()
{
  local _var_name="$1"
  local _result="$(printf %s $_var_name | awk -v RS=: -v ORS=: '!arr[$0]++')"
  echo $_result
  return 0
}

# Deduplicate path variables
bes-var-get()
{
  eval 'printf "%s\n" "${'"$1"'}"'
}

bes-var-set()
{
  eval "$1=\"\$2\""
}

bes-path-dedup()
{
  local _var_name="$1"
  local _value=$(bes-var-get $_var_name)
  bes-var-set $_var_name $(bes-path-remove-dups "$_value")
  return 0
}

bes-path-remove-trailing-colon()
{
  local _var_name="$1"
  local _value=$(bes-var-get $_var_name)
  bes-var-set $_var_name $(bes-path-remove-dups "$_value")
  return 0
}

function num_chars
{
  echo "${1}" | wc -c
}

#PATH=`printf %s "$PATH" | awk -v RS=: '{ if (!arr[$0]++) {printf("%s%s",!ln++?"":":",$0)}}'`
