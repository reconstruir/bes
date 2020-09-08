#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.system.host import host

class test_program_unit_test_true(program_unit_test):

  if host.is_unix():
    _program = program_unit_test.file_path(__file__, 'true.sh')
  elif host.is_windows():
    _program = program_unit_test.file_path(__file__, 'true.bat')
  else:
    host.raise_unsupported_system()
  
  def test_true(self):
    rv = self.run_program(self._program, [ 'foo', 'bar' ])
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( 'foo bar', rv.output )

  def test_true_raw(self):
    rv = self.run_program_raw(self._program, [ 'foo', 'bar' ])
    self.assertEqual( 0, rv.exit_code )
    self.assert_string_equal_strip( b'foo bar', rv.output )

class test_program_unit_test_false(program_unit_test):
  
  if host.is_unix():
    _program = program_unit_test.file_path(__file__, 'false.sh')
  elif host.is_windows():
    _program = program_unit_test.file_path(__file__, 'false.bat')
  else:
    host.raise_unsupported_system()
  
  def test_false(self):
    rv = self.run_program(self._program, [ 'foo', 'bar' ])
    self.assertEqual( 1, rv.exit_code )
    self.assert_string_equal_strip( 'foo bar', rv.output )

  def test_false_raw(self):
    rv = self.run_program_raw(self._program, [ 'foo', 'bar' ])
    self.assertEqual( 1, rv.exit_code )
    self.assert_string_equal_strip( b'foo bar', rv.output )

if __name__ == '__main__':
  program_unit_test.main()
