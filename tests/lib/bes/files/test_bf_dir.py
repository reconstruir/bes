#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.files.bf_dir import bf_dir
from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.files.match.bf_file_matcher_options import bf_file_matcher_options
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
    self.assertEqual( sorted(expected_files), self._list(tmp_dir, relative = False) )

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
    self.assertEqual( sorted(expected_files), self._list(tmp_dir) )

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
    self.assertEqual( [ 'kiwi.jpg' ], self._list(tmp_dir, patterns = ( '*.jpg', )) )
    self.assertEqual( [ 'kiwi.jpg', 'kiwi.png' ], self._list(tmp_dir, patterns = ( '*kiwi*', )) )

  def test_list_pattern_path_type_basename(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ])
    self.assertEqual( [], self._list(tmp_dir, patterns = ( 'kiwi*', ), path_type = 'absolute') )
    self.assertEqual( [ 'kiwi.jpg', 'kiwi.png' ], self._list(tmp_dir, patterns = ( 'kiwi*', ), path_type = 'basename') )
    
  def test_list_callable(self):
    tmp_dir = self._make_temp_content([
      'file foo.txt "foo.txt"',
      'file bar.txt "bar.txt"',
      'file kiwi.jpg "kiwi.jpg"',
      'file kiwi.png "kiwi.png"',
      'file orange.png "orange.png"',
      #'file emptyfile.txt',
      #'dir emptydir',
    ])
    self.assertEqual( [ 'kiwi.jpg' ], self._list(tmp_dir, callables = ( lambda entry_, filename_: filename_.endswith('.jpg'), )) )

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
    self.assertEqual( [ 'emptydir' ], bf_dir.list_dirs(tmp_dir, relative = True) )
    
  def xtest_all_parents(self):
    self.assertEqual( [ '/', '/usr', '/usr/lib' ], bf_dir.all_parents('/usr/lib/foo' ) )

  def _list(self, where, relative = True, patterns = None, expressions = None, callables = None, path_type = 'absolute'):
    match = bf_file_matcher(patterns = patterns,
                        expressions = expressions,
                        callables = callables)
    options = bf_file_matcher_options(path_type = path_type)
    entries = bf_dir.list(where, relative = relative, file_match = match, options = options)
    return entries.filenames()
    
if __name__ == '__main__':
  unit_test.main()
