#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.python.python_exe_filename import python_exe_filename
from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

class test_python_exe_filename(unit_test):

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_name_unix(self):
    self.assertEqual( 'python', python_exe_filename.name('/usr/bin/python') )
    self.assertEqual( 'python2', python_exe_filename.name('/usr/bin/python2') )
    self.assertEqual( 'python2.7', python_exe_filename.name('/usr/bin/python2.7') )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_name_windows(self):
    self.assertEqual( 'python', python_exe_filename.name(r'C:\Program Files\Python38\python.exe') )
    
if __name__ == '__main__':
  unit_test.main()
