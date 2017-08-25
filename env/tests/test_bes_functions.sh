#!/bin/bash

root()
{
  echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
  return 0
}

source $(root)/functions.sh
source $(root)/bes_testing.sh

function test_bes_path_dedup
{
  local P="foo:bar:foo:bar"
  bes_path_dedup P
  bes_assert "[ ${P} = foo:bar: ]"
}

function test_bes_path_remove_trailing_colon
{
  local P="foo:bar:"
  result=$(bes_path_remove_trailing_colon "foo:bar:")
  bes_assert "[ $result = foo:bar ]"
}

function test_bes_path_cleanup
{
  local P="foo:bar:foo:bar"
  bes_path_cleanup P
  bes_assert "[ ${P} = foo:bar ]"
}

bes_testing_run_unit_tests
exit $?

