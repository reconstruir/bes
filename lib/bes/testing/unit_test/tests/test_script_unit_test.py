#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import script_unit_test

class test_script_unit_test_true(script_unit_test):

  __script__ = __file__, '${test_data_dir}/bes.testing/unit_test/script_unit_test/true.sh'

  def test_true(self):
    rv = self.run_script([ 'foo', 'bar' ])
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( 'foo bar', rv.stdout )

  def test_true_raw(self):
    rv = self.run_script_raw([ 'foo', 'bar' ])
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( b'foo bar', rv.stdout )

class test_script_unit_test_false(script_unit_test):

  __script__ = __file__, '${test_data_dir}/bes.testing/unit_test/script_unit_test/false.sh'

  def test_false(self):
    rv = self.run_script([ 'foo', 'bar' ])
    self.assertEqual( 1, rv.exit_code )
    self.assert_string_equal_strip( 'foo bar', rv.stdout )

  def test_false_raw(self):
    rv = self.run_script_raw([ 'foo', 'bar' ])
    self.assertEqual( 1, rv.exit_code )
    self.assert_string_equal_strip( b'foo bar', rv.stdout )

if __name__ == '__main__':
  script_unit_test.main()
