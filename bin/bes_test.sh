#!/bin/bash

set -e

function main()
{
  local _this_dir="$(_bes_test_sh_this_dir)"
  cd ${_this_dir}/..
  local _root_dir=$(pwd)
  local _python_lib_dir="${_root_dir}/lib"
  local _site_lib_dir="${_root_dir}/VE/bes/lib/python3.11/site-packages"
  local _site_bin_dir="${_root_dir}/VE/bes/bin"
  export PATH="${_site_bin_dir}:${PATH}"
  export PYTHONPATH="${_site_lib_dir}:${_python_lib_dir}:${PYTHONPATH}"
  bin/bes_test.py bin/bes_test.py tests/lib/bes/btl/test_btl_document_base.py # ${1+"$@"}
  return 0
}

function _bes_test_sh_this_dir()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  return 0
}

function abs_to_rel_path() {
    local abs_path="$1"
    local current_dir="$(pwd)"
    local canonical_path="$(realpath "$abs_path")"
    local common_prefix="$(printf "%s\n%s\n" "$canonical_path" "$current_dir" | sed -e 'N;s/^\(.*\).*\n\1.*$/\1/')"
    local rel_path="${canonical_path#$common_prefix}"
    echo "$rel_path"
}

main ${1+"$@"}
