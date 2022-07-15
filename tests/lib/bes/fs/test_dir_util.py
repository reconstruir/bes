#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.fs.dir_util import dir_util
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

class test_dir_util(unit_test):

  def _make_temp_content(self, items):
    return temp_content.write_items_to_temp_dir(items, delete = not self.DEBUG)

  def test_list(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ])
    expected_files = [
      'foo.txt',
      'bar.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ]
    expected_files = [ path.join(tmp_dir, f) for f in expected_files ]
    self.assertEqual( sorted(expected_files), dir_util.list(tmp_dir) )

  def test_list_relative(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ])
    expected_files = [
      'foo.txt',
      'bar.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ]
    self.assertEqual( sorted(expected_files), dir_util.list(tmp_dir, relative = True) )

  def test_list_pattern(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ])
    self.assertEqual( [ 'kiwi.jpg' ], dir_util.list(tmp_dir, relative = True, patterns = '*.jpg') )
    self.assertEqual( [ 'kiwi.jpg', 'kiwi.png' ], dir_util.list(tmp_dir, relative = True, patterns = '*kiwi*') )

  def test_list_pattern_basename_is_true(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ])
    self.assertEqual( [], dir_util.list(tmp_dir, relative = True, patterns = 'kiwi*', basename = False) )
    self.assertEqual( [ 'kiwi.jpg', 'kiwi.png' ], dir_util.list(tmp_dir, relative = True, patterns = 'kiwi*', basename = True) )
    
  def test_list_function(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ])
    self.assertEqual( [ 'kiwi.jpg' ], dir_util.list(tmp_dir, relative = True, function = lambda f: f.endswith('.jpg')) )

  def test_list_dirs(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      'dir emptydir',
    ])
    self.assertEqual( [ path.join(tmp_dir, 'emptydir') ], dir_util.list_dirs(tmp_dir, relative = False) )

  def test_list_dirs_relative(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      'dir emptydir',
    ])
    self.assertEqual( [ 'emptydir' ], dir_util.list_dirs(tmp_dir, relative = True) )
    
  def test_all_parents(self):
    self.assertEqual( [ '/', '/usr', '/usr/lib' ], dir_util.all_parents('/usr/lib/foo' ) )

if __name__ == '__main__':
  unit_test.main()
