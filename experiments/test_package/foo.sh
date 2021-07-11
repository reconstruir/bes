#!/bin/bash

set -e

function main()
{
  echo "this is foo.sh"
  echo "args: "${1+"$@"}
  return 0
}

main ${1+"$@"}
