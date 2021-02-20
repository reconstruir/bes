#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.host import host
from bes.testing.program_unit_test import program_unit_test

class test_argparser_handler(program_unit_test):

  if host.is_unix():
    _program = program_unit_test.file_path(__file__, 'farm.py')
  elif host.is_windows():
    _program = program_unit_test.file_path(__file__, 'farm.bat')
  else:
    host.raise_unsupported_system()

  def test_fruit_order(self):
    rv = self.run_program(self._program, [ 'fruit', 'order', 'kiwi', '10' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '_command_fruit_order(fruit_type=kiwi, num=10, dry_run=False)', rv.output )
    
  def test_fruit_fail(self):
    rv = self.run_program(self._program, [ 'fruit', 'fail' ])
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( '_command_fruit_fail()', rv.output )

  def test_cheese_churn(self):
    rv = self.run_program(self._program, [ 'cheese', 'churn', '20' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '_command_cheese_churn(duration=20, dry_run=False)', rv.output )
    
  def test_cheese_fail(self):
    rv = self.run_program(self._program, [ 'cheese', 'fail' ])
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( '_command_cheese_fail()', rv.output )
    
  def test_version(self):
    rv = self.run_program(self._program, [ 'version', '--brief' ])
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_program(self._program, [ 'version', '--all' ])
    self.assertEqual( 0, rv.exit_code )
    
if __name__ == '__main__':
  program_unit_test.main()
