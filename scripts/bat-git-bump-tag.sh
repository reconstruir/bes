#!/bin/bash

set -e

function main()
{
  local _this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  local _bat_exe_run=${_this_dir}/bat-run-bat-exe.sh

  ${_bat_exe_run} "latest" git bump_tag
  
  return 0
}

main ${1+"$@"}
