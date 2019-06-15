#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.script_unit_test import script_unit_test
from bes.system.host import host

class test_script_unit_test_true(script_unit_test):

  if host.is_windows():
    __script__ = __file__, '${BES_TEST_DATA_DIR}/lib/bes/testing/script_unit_test/true.bat'
  elif host.is_unix():
    __script__ = __file__, '${BES_TEST_DATA_DIR}/lib/bes/testing/script_unit_test/true.sh'
  else:
    raise RuntimeError('unknown system')
  
  def test_true(self):
    rv = self.run_script([ 'foo', 'bar' ])
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( 'foo bar', rv.output )

  def test_true_raw(self):
    rv = self.run_script_raw([ 'foo', 'bar' ])
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( b'foo bar', rv.output )

class test_script_unit_test_false(script_unit_test):

  if host.is_windows():
    __script__ = __file__, '${BES_TEST_DATA_DIR}/lib/bes/testing/script_unit_test/false.bat'
  elif host.is_unix():
    __script__ = __file__, '${BES_TEST_DATA_DIR}/lib/bes/testing/script_unit_test/false.sh'
  else:
    raise RuntimeError('unknown system')
  
  def test_false(self):
    rv = self.run_script([ 'foo', 'bar' ])
    self.assertEqual( 1, rv.exit_code )
    self.assert_string_equal_strip( 'foo bar', rv.output )

  def test_false_raw(self):
    rv = self.run_script_raw([ 'foo', 'bar' ])
    self.assertEqual( 1, rv.exit_code )
    self.assert_string_equal_strip( b'foo bar', rv.output )

if __name__ == '__main__':
  script_unit_test.main()
