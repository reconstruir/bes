#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.fs.file_ignore import file_ignore
from bes.fs.testing.temp_content import temp_content

class test_file_ignore(unit_test):

  def test_should_ignore(self):
    tmp_dir = self._make_temp_content()
    a = file_ignore('.testing_test_ignore')
    self.assertFalse( a.should_ignore(path.join(tmp_dir, 'a/b/c/d/foo.txt')) )
    self.assertTrue( a.should_ignore(path.join(tmp_dir, 'a/b/c/d/bar.ttt')) )
    self.assertTrue( a.should_ignore(path.join(tmp_dir, 'a/b/c/d2/never.txt')) )
  
  def test_should_ignore_always_false(self):
    tmp_dir = self._make_temp_content()
    a = file_ignore(None)
    self.assertFalse( a.should_ignore(path.join(tmp_dir, 'a/b/c/d/foo.txt')) )
    self.assertFalse( a.should_ignore(path.join(tmp_dir, 'a/b/c/d/bar.ttt')) )
    self.assertFalse( a.should_ignore(path.join(tmp_dir, 'a/b/c/d2/never.txt')) )

  def _make_temp_content(self):
    return temp_content.write_items_to_temp_dir([
      'file a/b/c/.testing_test_ignore "d2\n\n" 644',
      'file a/b/c/d2/never.txt "this is never.txt\n" 644',
      'file a/b/c/d/bar.ttt "this is bar.ttt\n" 644',
      'file a/b/c/d/.testing_test_ignore "*.ttt\n" 644',
      'file a/b/c/d/foo.txt "this is foo.bar\n" 644',
    ], delete = not self.DEBUG)
  
if __name__ == '__main__':
  unit_test.main()
    
