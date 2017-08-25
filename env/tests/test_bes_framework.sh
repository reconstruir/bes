#!/bin/bash

source $_BES_DEV_ROOT/env/bes_framework.sh
source $_BES_DEV_ROOT/env/bes_testing.sh

function test_bes_var_set()
{
  bes_var_set FOO 666
  bes_assert "[ $FOO = 666 ]"
}

function test_bes_var_get()
{
  BAR=667
  v=$(bes_var_get BAR)
  bes_assert "[ $v = 667 ]"
}

bes_testing_run_unit_tests

