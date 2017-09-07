#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.test import script_tester

class test_script_tester_true(script_tester):

  __script__ = __file__, 'test_data/script_tester/true.sh'

  def test_true(self):
    rv = self.run_command('foo', 'bar')
    expected = 'foo bar'
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( expected, rv.stdout )

class test_script_tester_false(script_tester):

  __script__ = __file__, 'test_data/script_tester/false.sh'

  def test_false(self):
    rv = self.run_command('foo', 'bar')
    expected = 'foo bar'
    self.assertEqual( 1, rv.exit_code )
    self.assert_string_equal_strip( expected, rv.stdout )

if __name__ == '__main__':
  script_tester.main()
