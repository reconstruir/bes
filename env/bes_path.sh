
if [ -n "$_BES_TRACE" ]; then echo "bes_path.sh begin"; fi

export _BES_BASIC_PATH=$(env -i bash -c "echo ${PATH}")

export _BES_AWK=$(PATH=$_BES_BASIC_PATH which awk)
export _BES_CUT=$(PATH=$_BES_BASIC_PATH which cut)
export _BES_SED=$(PATH=$_BES_BASIC_PATH which sed)
export _BES_REV=$(PATH=$_BES_BASIC_PATH which rev)
export _BES_TR=$(PATH=$_BES_BASIC_PATH which tr)

export _BES_UNAME=$(PATH=$_BES_BASIC_PATH which uname)
export _BES_SYSTEM=$($_BES_UNAME | $_BES_TR '[:upper:]' '[:lower:]' | $_BES_SED 's/darwin/macos/')

# remove duplicates from a path
# from: https://unix.stackexchange.com/questions/14895/duplicate-entries-in-path-a-problem
function bes_path_dedup()
{
  if [ $# -ne 1 ]; then
    echo "Usage: bes_path_dedup path"
    return 1
  fi
  local path="$1"
  path=$(printf "%s" "${path}" | $_BES_AWK -v RS=':' '!a[$1]++ { if (NR > 1) printf RS; printf $1 }')
  echo "${path}"
  return 0
}

# sanitize a path by deduping entries and stripping leading or trailing colons
function bes_path_sanitize()
{
  if [ $# -ne 1 ]; then
    echo "Usage: bes_path_dedup path"
    return 1
  fi
  local path=$(bes_path_dedup "$1")
  local first=$(printf "%s" "${path}" | $_BES_CUT -c 1)
  if [[ "${first}" == ":" ]]; then
    path=$(printf "%s" "${path}" | $_BES_CUT -b 2-)
  fi
  local reversed=$(printf "%s" "${path}" | $_BES_REV)
  local last=$(printf "%s" "${reversed}" | $_BES_CUT -c 1)
  if [[ "${last}" == ":" ]]; then
    path=$(printf "%s" "${reversed}" | $_BES_CUT -b 2- | $_BES_REV)
  fi
  echo "${path}"
  return 0
}

function bes_path_remove()
{
  if [ $# -lt 2 ]; then
    echo "Usage: bes_path_remove path p1 p2 ... pN"
    return 1
  fi
  local path="$1"
  shift
  local what
  local result="${path}"
  while [[ $# > 0 ]]; do
    what="$1"
    result="${what}":"${result}"
    result=$(printf "%s" "${result}" | $_BES_AWK -v RS=: -v ORS=: -v what="^${what}$" '$0~what {next} {print}')
    shift
  done
  echo $(bes_path_sanitize "${result}")
  return 0
}

function bes_path_append()
{
  if [ $# -lt 2 ]; then
    echo "Usage: bes_path_append path p1 p2 ... pN"
    return 1
  fi
  local path="$1"
  shift
  local what
  local result="${path}"
  while [[ $# > 0 ]]; do
    what="$1"
    result=$(bes_path_remove "${result}" "${what}")
    result="${result}":"${what}"
    shift
  done
  result=$(bes_path_sanitize "${result}")
  echo "${result}"
  return 0
}

function bes_path_prepend()
{
  if [ $# -lt 2 ]; then
    echo "Usage: bes_path_prepend path p1 p2 ... pN"
    return 1
  fi
  local path="$1"
  shift
  local what
  local result="${path}"
  while [[ $# > 0 ]]; do
    what="$1"
    result="${what}":"${result}"
    shift
  done
  echo $(bes_path_sanitize "${result}")
  return 0
}

function bes_path_print()
{
  if [[ $# != 1 ]]; then
    echo "Usage: bes_path_print path"
    return 1
  fi
  local pa=(`set -f; IFS=:; printf "%s\n" $PATH`)
  for item in ${pa[@]}; do
    echo "${item}"
  done
  return 0
}

function bes_env_path_cleanup()
{
  local _var_name="$1"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_sanitize "$_value")
  bes_var_set $_var_name "$_new_value"
  return 0
}

function bes_env_path_append()
{
  local _var_name="$1"
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_append "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_prepend()
{
  local _var_name="$1"
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_prepend "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_remove()
{
  local _var_name="$1"
  shift
  local _parts="$@"
  local _value=$(bes_var_get $_var_name)
  local _new_value=$(bes_path_remove "$_value" "$_parts")
  bes_var_set $_var_name "$_new_value"
  export $_var_name
  return 0
}

function bes_env_path_clear()
{
  local _var_name="$1"
  bes_var_set $_var_name ""
  export $_var_name
  return 0
}

if [ -n "$_BES_TRACE" ]; then echo "bes_path.sh end"; fi
