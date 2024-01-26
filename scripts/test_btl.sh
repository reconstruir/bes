#!/bin/bash

#set -e

function main()
{
  source $(_test_btl_this_dir)/../bes_bash/bes_bash.bash

  if [[ $# < 2 ]]; then
    echo "Usage: test_btl.sh btl_filename test_filename [ test_function ]"
    return 1
  fi

  local _btl_basename=${1}
  local _test_basename=${2}
  local _test_function=${3}

  local _btl_filename=$(find lib/bes tests/lib/bes -name ${_btl_basename})
  if [ ! -f "${_btl_filename}" ]; then
    echo "test_btl.sh: BTL file not found: ${_btl_basename}"
    return 1
  fi
  local _test_filename=$(find tests/lib/bes -name ${_test_basename})
  if [ ! -f "${_test_filename}" ]; then
    echo "test_test.sh: Test file not found: ${_test_basename}"
    return 1
  fi

  local _test_function_arg=""
  if [ ! -z "${_test_function}" ]; then
    _test_function_arg=":${_test_function}"
  fi

  local _make_dir=$(dirname ${_btl_filename})

  #echo _btl_filename=${_btl_filename}
  #echo _test_filename=${_test_filename}
  #echo _test_function=${_test_function}
  #echo _test_function_arg=${_test_function_arg}
  #echo _make_dir=${_make_dir}
  local _log=$(mktemp).log
  trap 'rm -f "${_log}"' EXIT
  #echo _log=${_log}
  
  make -C ${_make_dir} all >& ${_log}
  local _make_rv=$?
  #echo _make_rv=${_make_rv}
  if [[ ${_make_rv} != 0 ]]; then
    cat ${_log}
    return ${_make_rv}
  fi

  local _log_tag=${_btl_basename%.*}
  local _bes_log="${_log_tag}=debug format=brief"
  local _bes_test=$(bes_path_abs_file $(_test_btl_this_dir)/../bin/bes_test.py)
  #echo _bes_log=${_bes_log}
  
  DEBUG=1 BES_LOG="${_bes_log}" ${_bes_test} --dont-hack-env ${_test_filename} ${_test_function_arg} >& ${_log}
  local _test_rv=$?
  if [[ ${_test_rv} != 0 ]]; then
    less ${_log}
    return ${_test_rv}
  fi
  return 0
}

function _test_btl_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

main ${1+"$@"}
