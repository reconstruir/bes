#!/bin/bash

source $_BES_DEV_ROOT/env/bes_path.sh
source $_BES_DEV_ROOT/env/bes_testing.sh

function test_bes_path_append()
{
  bes_assert "[ $(bes_path_append foo bar) = foo:bar ]"
  bes_assert "[ $(bes_path_append foo bar bar foo) = foo:bar ]"
}

function test_bes_path_prepend()
{
  bes_assert "[ $(bes_path_prepend foo bar) = bar:foo ]"
  bes_assert "[ $(bes_path_prepend foo bar bar foo) = bar:foo ]"
}

function test_bes_path_cleanup()
{
  bes_assert "[ $(bes_path_cleanup :a::::b:) = a:b ]"
  bes_assert "[ $(bes_path_cleanup a:b:c:a:b:c) = a:b:c ]"
}

bes_testing_run_unit_tests

