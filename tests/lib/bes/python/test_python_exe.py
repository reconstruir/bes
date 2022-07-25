#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.file_util import file_util
from bes.python.python_error import python_error
from bes.python.python_exe import python_exe
from bes.python.python_testing import python_testing
from bes.system.env_override import env_override
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_python_exe(unit_test):

  def test_full_version(self):
    fake_exe = python_testing.make_temp_fake_python('python', '2.7.666', debug = self.DEBUG)
    self.assertEqual( '2.7.666', str(python_exe.full_version(fake_exe)) )

  def test_version(self):
    fake_exe = python_testing.make_temp_fake_python('python', '2.7.666', debug = self.DEBUG)
    self.assertEqual( '2.7', str(python_exe.version(fake_exe)) )

  def test_check_exe_success(self):
    fake_exe = python_testing.make_temp_fake_python('python6.7', '6.7.666', debug = self.DEBUG)
    self.assertEqual( '6.7.666', python_exe.check_exe(fake_exe) )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_check_exe_not_executable(self):
    fake_exe = python_testing.make_temp_fake_python('python6.7', '6.7.666', mode = 0o0600, debug = self.DEBUG)
    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe(fake_exe)
    self.assertTrue( 'not a valid executable' in str(ctx.exception) )
    
  def test_check_exe_not_abs(self):
    with self.assertRaises(python_error) as ctx:
      python_exe.check_exe('python6.7')
    self.assertTrue( 'not an absolute path' in str(ctx.exception) )

if __name__ == '__main__':
  unit_test.main()
