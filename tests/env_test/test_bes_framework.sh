#!/bin/bash

source $_BES_DEV_ROOT/env/bes_framework.sh

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

function xtest_bes_array_to_string()
{
  v=$(bes_array_to_string "foo" "bar" "apple and kiwi")
  bes_assert '[ $v = ([0]="foo" [1]="bar" [2]="apple and kiwi") ]'
}

function test_bes_path_dedup()
{
  bes_assert "[ $(bes_path_dedup /bin:/foo:/bin) = /bin:/foo ]"
  bes_assert "[ $(bes_path_dedup /bin:/bin:/bin) = /bin ]"
  bes_assert "[ $(bes_path_dedup /bin::/bin:/bin) = /bin: ]"
  bes_assert "[ $(bes_path_dedup /bin::/bin:/bin:::) = /bin: ]"
  bes_assert "[ $(bes_path_dedup \"\") = \"\" ]"
  bes_assert "[ $(bes_path_dedup /bin:/foo/bin:/bin) = /bin:/foo/bin ]"
#  bes_assert "[ $(bes_path_dedup /bin:/foo/bin:/bin:/a\ b) = /bin:/foo/bin:/a\ b ]"
}

function test_bes_path_sanitize()
{
  bes_assert "[ $(bes_path_sanitize /bin:/foo:/bin) = /bin:/foo ]"
  bes_assert "[ $(bes_path_sanitize /bin:/bin:/bin) = /bin ]"
  bes_assert "[ $(bes_path_sanitize :/bin) = /bin ]"
  bes_assert "[ $(bes_path_sanitize /bin::/bin:/bin:::) = /bin ]"
  bes_assert "[ $(bes_path_sanitize \"\") = \"\" ]"
  bes_assert "[ $(bes_path_sanitize :a::::b:) = a:b ]"
  bes_assert "[ $(bes_path_sanitize a:b:c:a:b:c) = a:b:c ]"
#  bes_assert "[ $(bes_path_sanitize a\ b:c\ d) = a\ b:c\ d ]"
}

function test_bes_path_append()
{
  bes_assert "[ $(bes_path_append /bin /foo/bin) = /bin:/foo/bin ]"
  bes_assert "[ $(bes_path_append /bin:/foo/bin /foo/bin) = /bin:/foo/bin ]"
  bes_assert "[ $(bes_path_append /bin:/foo/bin /foo/bin /bar/bin) = /bin:/foo/bin:/bar/bin ]"
  bes_assert "[ $(bes_path_append /bin:/foo/bin /bin) = /foo/bin:/bin ]"
  bes_assert "[ $(bes_path_append foo bar) = foo:bar ]"
  bes_assert "[ $(bes_path_append foo bar bar foo) = bar:foo ]"
#  bes_assert "[ $(bes_path_append /bin:/foo/bin '/a b') = '/foo/bin:/bin:/a b' ]"
}

function test_bes_path_prepend()
{
  bes_assert "[ $(bes_path_prepend /bin /foo/bin) = /foo/bin:/bin ]"
  bes_assert "[ $(bes_path_prepend /foo/bin:/bin /foo/bin) = /foo/bin:/bin ]"
  bes_assert "[ $(bes_path_prepend /foo/bin:/bin /bin) = /bin:/foo/bin ]"
#  bes_assert "[ $(bes_path_prepend /foo/bin:/bin /a\ b) = /a\ b:/foo/bin:/bin ]"
}

function test_bes_path_remove()
{
  bes_assert "[ $(bes_path_remove /bin:/foo/bin /foo/bin) = /bin ]"
  bes_assert "[ $(bes_path_remove /bin:/foo/bin foo/bin) = /bin:/foo/bin ]"
  bes_assert "[ $(bes_path_remove foo:bar bar) = foo ]"
  bes_assert "[ $(bes_path_remove foo:bar bar foo) = ]"
  bes_assert "[ $(bes_path_remove "foo:a b:bar" bar = "foo:a b") ]"
}

function test_bes_env_path_append()
{
  local _SAVE_PATH="${PATH}"
  PATH=/foo ; bes_env_path_append PATH /bar ; bes_assert "[ ${PATH} = /foo:/bar ]"
  PATH="${_SAVE_PATH}"
}

function test_bes_env_path_prepend()
{
  local _SAVE_PATH="${PATH}"
  PATH=/foo ; bes_env_path_prepend PATH /bar ; bes_assert "[ ${PATH} = /bar:/foo ]"
  PATH="${_SAVE_PATH}"
}

function test_bes_env_path_remove()
{
  local _SAVE_PATH="${PATH}"
  PATH=/foo:/bar ; bes_env_path_remove PATH /bar ; bes_assert "[ ${PATH} = /foo ]"
  PATH="${_SAVE_PATH}"
}

function test_bes_variable_map_linux()
{
  if [[ $(bes_system) != 'linux' ]]; then
    return 0
  fi
  bes_assert "[ $(bes_variable_map PATH) = PATH ]"
  bes_assert "[ $(bes_variable_map PYTHONPATH) = PYTHONPATH ]"
  bes_assert "[ $(bes_variable_map LD_LIBRARY_PATH) = LD_LIBRARY_PATH ]"
  bes_assert "[ $(bes_variable_map DYLD_LIBRARY_PATH) = LD_LIBRARY_PATH ]"
}

function test_bes_variable_map_macos()
{
  if [[ $(bes_system) != 'macos' ]]; then
    return 0
  fi
  bes_assert "[ $(bes_variable_map PATH) = PATH ]"
  bes_assert "[ $(bes_variable_map PYTHONPATH) = PYTHONPATH ]"
  bes_assert "[ $(bes_variable_map LD_LIBRARY_PATH) = DYLD_LIBRARY_PATH ]"
  bes_assert "[ $(bes_variable_map DYLD_LIBRARY_PATH) = DYLD_LIBRARY_PATH ]"
}

function test_bes_source_dir()
{
  local _pid=$$
  local _tmp=/tmp/test_bes_source_dir_${_pid}
  mkdir -p ${_tmp}
  echo "FOO=foo_${_pid}" > $_tmp/1.sh
  echo "BAR=bar_${_pid}" > $_tmp/2.sh
  echo "BAZ=baz_${_pid}" > $_tmp/3.sh
  (
    bes_source_dir ${_tmp}
    bes_assert "[ ${FOO} = foo_${_pid} ]"
    bes_assert "[ ${BAR} = bar_${_pid} ]"
    bes_assert "[ ${BAZ} = baz_${_pid} ]"
  )
  rm -rf ${_tmp}
}  

function test_bes_to_lower()
{
  bes_assert "[[ $(bes_to_lower FoO) == foo ]]"
  bes_assert "[[ $(bes_to_lower FOO) == foo ]]"
  bes_assert "[[ $(bes_to_lower foo) == foo ]]"
}  

function test_bes_is_true()
{
  function _call_is_true() ( if $(bes_is_true $*); then echo yes; else echo no; fi )
  bes_assert "[[ $(_call_is_true true) == yes ]]"
  bes_assert "[[ $(_call_is_true True) == yes ]]"
  bes_assert "[[ $(_call_is_true TRUE) == yes ]]"
  bes_assert "[[ $(_call_is_true tRuE) == yes ]]"
  bes_assert "[[ $(_call_is_true 1) == yes ]]"
  bes_assert "[[ $(_call_is_true t) == yes ]]"
  bes_assert "[[ $(_call_is_true too) == no ]]"
  bes_assert "[[ $(_call_is_true false) == no ]]"
  bes_assert "[[ $(_call_is_true 0) == no ]]"
}  

function xtest_bes_dirname()
{
  bes_assert "[[ $(bes_dirname foo) == foo ]]"
  bes_assert "[[ $(bes_dirname foo/bar) == foo ]]"
  bes_assert "[[ $(bes_dirname foo/bar.png) == foo ]]"
  bes_assert "[[ $(bes_dirname /foo/bar.png) == foo ]]"
  bes_assert "[[ $(bes_dirname /) == / ]]"
}  

bes_testing_run_unit_tests
