#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import os.path as path

from bes.system.host import host
from bes.testing.script_unit_test import script_unit_test

class test_argparser_handler(script_unit_test):

  if host.is_unix():
    __script__ = __file__, 'farm.py'
  elif host.is_windows():
    __script__ = __file__, 'farm.bat'
  else:
    host.raise_unsupported_system()

  def test_fruit_order(self):
    rv = self.run_script([ 'fruit', 'order', 'kiwi', '10' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '_command_fruit_order(fruit_type=kiwi, num=10, dry_run=False)', rv.output )
    
  def test_fruit_fail(self):
    rv = self.run_script([ 'fruit', 'fail' ])
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( '_command_fruit_fail()', rv.output )

  def test_cheese_churn(self):
    rv = self.run_script([ 'cheese', 'churn', '20' ])
    self.assertEqual( 0, rv.exit_code )
    self.assertEqual( '_command_cheese_churn(duration=20, dry_run=False)', rv.output )
    
  def test_cheese_fail(self):
    rv = self.run_script([ 'cheese', 'fail' ])
    self.assertEqual( 1, rv.exit_code )
    self.assertEqual( '_command_cheese_fail()', rv.output )
    
    
  def xtest_version(self):
    rv = self.run_script([ 'version', '--brief' ])
    self.assertEqual( 0, rv.exit_code )

    rv = self.run_script([ 'version', '--all' ])
    self.assertEqual( 0, rv.exit_code )
    
if __name__ == '__main__':
  script_unit_test.main()
