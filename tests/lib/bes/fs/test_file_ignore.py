#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_ignore as FI, ignore_file_data as IFD, temp_file

class test_ignore_file_data(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.fs/file_ignore'
  
  def test__init__(self):
    self.assertEqual( ( '/tmp/foo', [ '*.txt' ] ), IFD('/tmp/foo', [ '*.txt' ]) )
  
  def test_read_file(self):
    content = '''
# comment
*.txt
*.png
foobar # comment
'''
    tmp = temp_file.make_temp_file(content = content)
    self.assertEqual( ( path.dirname(tmp), [ '*.txt', '*.png', 'foobar' ] ), IFD.read_file(tmp) )
  
  def test_should_ignore(self):
    content = '''
# comment
*.txt
*.png
foobar # comment
'''
    tmp = temp_file.make_temp_file(content = content)
    a = IFD.read_file(tmp)
    self.assertTrue( a.should_ignore('ppp.txt') )
    self.assertTrue( a.should_ignore('foo.png') )
    self.assertTrue( a.should_ignore('foobar') )
    self.assertFalse( a.should_ignore('ppp.pdf') )
    self.assertFalse( a.should_ignore('foo.jpg') )
    self.assertFalse( a.should_ignore('foobarx') )
  
class test_file_ignore(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.fs/file_ignore'
  
  def test_basic(self):
    a = FI('.bes_test_ignore')
    a.ignore(self.data_path('a/b/c/d/foo.txt'))
  
if __name__ == '__main__':
  unit_test.main()
    
