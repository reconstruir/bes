#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.python.python_exe_config import python_exe_config
from bes.testing.unit_test import unit_test

class test_python_exe_config(unit_test):

  def test_empty_file(self):
    tmp = self.make_temp_file(suffix = '.python_config')
    c = python_exe_config(tmp)
    self.assertEqual( None, c.get_python_exe('3.7', system = 'macos') )

  def test_existing_file(self):
    content = '''\
macos
  2.7: /usr/bin/python2.7
  3.7: /usr/local/opt/python@3.7/bin/python3.7
  3.8: /usr/local/opt/python@3.8/bin/python3.8
  3.9: /usr/local/opt/python@3.9/bin/python3.9

windows
  2.7: C:\Python27\python.exe
  3.7: C:\Program Files\Python37\python.exe
  3.8: C:\Program Files\Python38\python.exe
  3.9: C:\Program Files\Python39\python.exe
'''
    tmp = self.make_temp_file(content = content, suffix = '.python_config')
    c = python_exe_config(tmp)
    self.assertEqual( '/usr/local/opt/python@3.7/bin/python3.7', c.get_python_exe('3.7', system = 'macos') )
    self.assertEqual( r'C:\Program Files\Python37\python.exe', c.get_python_exe('3.7', system = 'windows') )
    
  def xtest_change_python_exe(self):
    content = '''\
pip_project
  python_exe: /foo/bin/python666.exe
'''
    tmp = self.make_temp_file(content = content, suffix = '.pip_project')
    c = python_exe_config(tmp)
    self.assertEqual( '/foo/bin/python666.exe', c.python_exe )
    c.python_exe = '/foo/bin/python667.exe'
    expected = '''\
pip_project
  python_exe: /foo/bin/python667.exe
'''
    self.assert_text_file_equal( expected, tmp, native_line_breaks = True )
    
if __name__ == '__main__':
  unit_test.main()
