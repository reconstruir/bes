#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tempfile
from bes.testing.unit_test import unit_test
from bes.fs.testing import temp_item as I

class test_temp_item(unit_test):

  def test_parse_string(self):
    self.assertEqual( I( I.FILE, 'foo.txt', 'this is foo\nhaha', None ), I.parse('file foo.txt "this is foo\nhaha"') )
    self.assertEqual( ( I.FILE, 'foo.txt', None, None ), I.parse('file foo.txt') )
    self.assertEqual( ( I.DIR, 'foo', None, None ), I.parse('dir foo') )
    self.assertEqual( ( I.FILE, 'foo.txt', None, 0755 ), I.parse('file foo.txt "" 755') )

  def test_parse_tuple(self):
    self.assertEqual( ( I.FILE, 'foo.txt', None, None ), I.parse( ('file', 'foo.txt' ) ) )
    self.assertEqual( ( I.FILE, 'foo.txt', 'this is foo\nhaha', None ), I.parse( ('file', 'foo.txt', 'this is foo\nhaha') ) )

  def test_write(self):
    i = I(I.FILE, 'foo.txt', 'this is foo\nhaha', 0644)
    tmp_dir = tempfile.mkdtemp()
    i.write(tmp_dir)
    p = path.join(tmp_dir, 'foo.txt')
    self.assertTrue( path.exists(p) )
    self.assertEqual( 0644, os.stat(p).st_mode & 0777 )
    with open(p, 'r') as fin:
      self.assertEqual( 'this is foo\nhaha', fin.read() )

  def test_parse_sequence(self):
    expected = (
      ( 'file', 'foo.txt', 'foo content', 0755 ),
      ( 'file', 'bar.txt', 'bar content', 0644 ),
      ( 'dir', 'baz', None, 0700 ),
    )
      
    self.assertEqual( expected, I.parse_sequence([
      'file foo.txt "foo content" 755',
      'file bar.txt "bar content" 644',
      'dir  baz     ""            700',
    ]) )
      
if __name__ == "__main__":
  unit_test.main()
