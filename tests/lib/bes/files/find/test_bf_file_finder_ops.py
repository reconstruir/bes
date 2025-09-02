#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
#from collections import namedtuple

#from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.files.find.bf_file_finder_ops import bf_file_finder_ops
#from bes.files.find.bf_file_finder_options import bf_file_finder_options
#from bes.files.bf_entry import bf_entry
#from bes.files.bf_entry_list import bf_entry_list
from bes.fs.testing.temp_content import temp_content
from bes.system.log import logger

from bes.testing.unit_test import unit_test

class test_bf_file_finder_ops(unit_test):

  _log = logger('bf_file_finder')
  
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)
  
  def test_find_dirs(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    tmp_dir = self._make_temp_content(content)
    self.assert_filename_list_equal( [
      'emptydir',
      'subdir',
      'subdir/subberdir',
    ], bf_file_finder_ops.find_dirs(tmp_dir).relative_filenames(sort = True) )

  def test_find_files(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    tmp_dir = self._make_temp_content(content)
    self.assert_filename_list_equal( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], bf_file_finder_ops.find_files(tmp_dir).relative_filenames(sort = True) )
    
if __name__ == '__main__':
  unit_test.main()
