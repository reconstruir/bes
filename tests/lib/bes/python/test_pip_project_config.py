#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.pip.pip_project_config import pip_project_config
from bes.testing.unit_test import unit_test

class test_pip_project_config(unit_test):

  def test_empty_file(self):
    tmp = self.make_temp_file(suffix = '.pip_project')
    c = pip_project_config(tmp)
    self.assertEqual( None, c.python_exe )

  def test_existing_file(self):
    content = '''\
pip_project
  python_exe: /foo/bin/python.exe
'''
    tmp = self.make_temp_file(content = content, suffix = '.pip_project')
    c = pip_project_config(tmp)
    self.assertEqual( '/foo/bin/python.exe', c.python_exe )
    
  def test_change_python_exe(self):
    content = '''\
pip_project
  python_exe: /foo/bin/python666.exe
'''
    tmp = self.make_temp_file(content = content, suffix = '.pip_project')
    c = pip_project_config(tmp)
    self.assertEqual( '/foo/bin/python666.exe', c.python_exe )
    c.python_exe = '/foo/bin/python667.exe'
    expected = '''\
pip_project
  python_exe: /foo/bin/python667.exe
'''
    self.assert_text_file_equal( expected, tmp, native_line_breaks = True )
    
if __name__ == '__main__':
  unit_test.main()
