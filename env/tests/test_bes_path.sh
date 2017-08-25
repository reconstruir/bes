#!/bin/bash

source $BES_ROOT/env/bes_path.sh
source $BES_ROOT/env/bes_testing.sh

function test_bes_path_append()
{
  local rv=$(bes_path_append foo bar)
  bes_assert "[ ${rv} = foo:bar ]"
}

bes_testing_run_unit_tests

