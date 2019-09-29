#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.testing.script_unit_test import script_unit_test
from bes.system.host import host

class test_command_cli(script_unit_test):

  if host.is_unix():
    __script__ = __file__, 'fake_script.py'
  elif host.is_windows():
    __script__ = __file__, 'fake_script.bat'
  else:
    host.raise_unsupported_system()
  
  def test_foo(self):
    rv = self.run_script([ 'foo', 'address', 'version' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'foo:address:version:0:0', rv.output )
    
  def test_bar(self):
    rv = self.run_script([ 'bar', 'branch', '--verbose' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( 'bar:branch:1', rv.output )
    
  def test_version(self):
    rv = self.run_script([ 'version', '--brief' ])
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_script([ 'version', '--all' ])
    self.assertEqual( 0, rv.exit_code )
    
if __name__ == '__main__':
  script_unit_test.main()
