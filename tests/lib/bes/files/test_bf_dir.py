#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

import os.path as path
from bes.files.bf_dir import bf_dir
from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

class test_bf_dir(unit_test):

  def _make_temp_content(self, items):
    return temp_content.write_items_to_temp_dir(items, delete = not self.DEBUG)

  def test_is_empty_true(self):
    tmp_dir = self.make_temp_dir()
    self.assertEqual( True, bf_dir.is_empty(tmp_dir) )

  def test_is_empty_false(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
    ])
    self.assertEqual( False, bf_dir.is_empty(tmp_dir) )
    
  def test_list_absolute(self):
    content = [
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
    ]
    t = self._call_list(content, relative = False)
    expected_filenames = [
      'bar.txt',
      'foo.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ]
    expected_filenames = sorted([ path.join(t.tmp_dir, f) for f in expected_filenames ])
    self.assertEqual( expected_filenames, t.filenames )

  def test_list_relative(self):
    content = [
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
    ]
    t = self._call_list(content, relative = True)
    self.assertEqual( [
      'bar.txt',
      'foo.txt',
      'kiwi.jpg',
      'kiwi.png',
      'orange.png',
    ], t.filenames )

  def test_list_with_pattern(self):
    content = [
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
    ]
    t = self._call_list(content, relative = True,
                        matcher = bf_file_matcher(patterns = ( '*.jpg', )))
    self.assertEqual( [
      'kiwi.jpg',
    ], t.filenames )
    t = self._call_list(content, relative = True,
                        matcher = bf_file_matcher(patterns = ( '*kiwi*', )))
    self.assertEqual( [
      'kiwi.jpg',
      'kiwi.png',
    ], t.filenames )

  def test_list_with_pattern_path_type_absolute(self):
    content = [
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ]
    matcher = bf_file_matcher()
    matcher.add_item_fnmatch('kiwi*', path_type = 'absolute')
    t = self._call_list(content, relative = True, matcher = matcher)
    self.assertEqual( [], t.filenames )
    
  def test_list_with_pattern_path_type_basename(self):
    content = [
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ]
    matcher = bf_file_matcher()
    matcher.add_item_fnmatch('kiwi*', path_type = 'basename')
    t = self._call_list(content, relative = True, matcher = matcher)
    self.assertEqual( [ 'kiwi.jpg', 'kiwi.png' ], t.filenames )
    
  def test_list_with_callable(self):
    content = [
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
    ]
    t = self._call_list(content, relative = True,
                        matcher = bf_file_matcher(callables = ( lambda f: f.endswith('.jpg'), )))
    self.assertEqual( [
      'kiwi.jpg',
    ], t.filenames )
    t = self._call_list(content, relative = True,
                        matcher = bf_file_matcher(patterns = ( '*kiwi*', )))

  def xtest_list_dirs(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      'dir emptydir',
    ])
    self.assertEqual( [ path.join(tmp_dir, 'emptydir') ], bf_dir.list_dirs(tmp_dir, relative = False) )

  def xtest_list_dirs_relative(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      'dir emptydir',
    ])
    self.assertEqual( [ 'emptydir' ], bf_dir.list_dirs(tmp_dir) )
    
  def xtest_all_parents(self):
    self.assertEqual( [ '/', '/usr', '/usr/lib' ], bf_dir.all_parents('/usr/lib/foo' ) )

  _test_result = namedtuple('_test_result', 'tmp_dir, filenames')
  def _call_list(self, content, **kwargs):
    tmp_dir = self._make_temp_content(content)
    filenames = bf_dir.list(tmp_dir, **kwargs)
    return self._test_result(tmp_dir, filenames)
  
if __name__ == '__main__':
  unit_test.main()
