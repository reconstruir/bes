#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.files.ignore.bf_file_ignore import bf_file_ignore_item
from bes.files.bf_entry import bf_entry

class test_bf_file_ignore_item(unit_test):
  
  def test__init__(self):
    self.assertEqual( ( '/tmp/foo', [ '*.txt' ] ), bf_file_ignore_item('/tmp/foo', [ '*.txt' ]) )
  
  def test_read_file(self):
    content = '''
# comment
*.txt
*.png
foobar # comment
'''
    tmp = self.make_temp_file(content = content)
    self.assertEqual( ( path.dirname(tmp), [ '*.txt', '*.png', 'foobar' ] ), bf_file_ignore_item.read_file(tmp) )
  
  def test_should_ignore(self):
    content = '''
# comment
*.txt
*.png
foobar # comment
'''
    tmp = self.make_temp_file(content = content)
    a = bf_file_ignore_item.read_file(tmp)
    self.assertTrue( a.should_ignore(bf_entry('ppp.txt'), '/tmp') )
    self.assertTrue( a.should_ignore(bf_entry('foo.png'), '/tmp') )
    self.assertTrue( a.should_ignore(bf_entry('foobar'), '/tmp') )
    self.assertFalse( a.should_ignore(bf_entry('ppp.pdf'), '/tmp') )
    self.assertFalse( a.should_ignore(bf_entry('foo.jpg'), '/tmp') )
    self.assertFalse( a.should_ignore(bf_entry('foobarx'), '/tmp') )
  
if __name__ == '__main__':
  unit_test.main()
    
