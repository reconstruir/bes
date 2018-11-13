#!/bin/bash

source $_BES_DEV_ROOT/env/bes_caca.sh
source $_BES_DEV_ROOT/env/bes_testing.sh

function test_bes_caca_print()
{
  bes_assert "[ $(bes_caca_print) = foo ]"
}

bes_testing_run_unit_tests

