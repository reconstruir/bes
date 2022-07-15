#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_ignore import file_ignore_item

class test_file_ignore_item(unit_test):
  
  def test__init__(self):
    self.assertEqual( ( '/tmp/foo', [ '*.txt' ] ), file_ignore_item('/tmp/foo', [ '*.txt' ]) )
  
  def test_read_file(self):
    content = '''
# comment
*.txt
*.png
foobar # comment
'''
    tmp = self.make_temp_file(content = content)
    self.assertEqual( ( path.dirname(tmp), [ '*.txt', '*.png', 'foobar' ] ), file_ignore_item.read_file(tmp) )
  
  def test_should_ignore(self):
    content = '''
# comment
*.txt
*.png
foobar # comment
'''
    tmp = self.make_temp_file(content = content)
    a = file_ignore_item.read_file(tmp)
    self.assertTrue( a.should_ignore('ppp.txt') )
    self.assertTrue( a.should_ignore('foo.png') )
    self.assertTrue( a.should_ignore('foobar') )
    self.assertFalse( a.should_ignore('ppp.pdf') )
    self.assertFalse( a.should_ignore('foo.jpg') )
    self.assertFalse( a.should_ignore('foobarx') )
  
if __name__ == '__main__':
  unit_test.main()
    
