#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.testing.program_unit_test import program_unit_test
from bes.system.host import host

class test_command_cli(program_unit_test):

  if host.is_unix():
    _program = program_unit_test.file_path(__file__, 'fake_program.py')
  elif host.is_windows():
    _program = program_unit_test.file_path(__file__, 'fake_program.bat')
  else:
    host.raise_unsupported_system()
  
  def test_foo(self):
    rv = self.run_program(self._program, [ 'foo', 'address', 'version' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo:address:version:0:0', rv.output )
    
  def test_bar(self):
    rv = self.run_program(self._program, [ 'bar', 'branch', '--verbose' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'bar:branch:1', rv.output )
    
  def test_version(self):
    rv = self.run_program(self._program, [ 'version', '--brief' ])
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_program(self._program, [ 'version', '--all' ])
    self.assertEqual( 0, rv.exit_code )
    
if __name__ == '__main__':
  program_unit_test.main()
