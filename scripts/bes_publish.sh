#!/bin/bash

set -e

function main()
{
  local _this_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
  local _root_dir="$(cd "${_this_dir}/.." && pwd)"
  local _bat_sh="${_root_dir}/../bat/bin/bat.sh"

  # e.g.: bes_publish.sh
  # e.g.: bes_publish.sh --allow-untagged
  # e.g.: bes_publish.sh --target pypi-org
  "${_bat_sh}" pypi -r "${_root_dir}" publish ${1+"$@"}

  return 0
}

main ${1+"$@"}
