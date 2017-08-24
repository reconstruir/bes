#!/bin/bash

root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

source $(root)/functions.sh
source $(root)/bes_testing.sh

function test_num_chars
{
  local res=$(num_chars "foo")
  bes_assert "[ ${res} -eq 4 ]"
}

bes_testing_run_unit_tests
exit $?

