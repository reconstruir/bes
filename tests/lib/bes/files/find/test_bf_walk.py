#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.files.bf_entry import bf_entry
from bes.files.bf_entry_list import bf_entry_list
from bes.files.find.bf_walk import bf_walk
from bes.files.match.bf_file_matcher import bf_file_matcher
from bes.fs.testing.temp_content import temp_content
from bes.system.log import logger

from bes.testing.unit_test import unit_test

class test_bf_walk(unit_test):

  _log = logger('bf_walk')
  
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  _walk_result = namedtuple('_walk_result', 'tmp_dir, result')
  def _walk(self, items, **kwargs):
    tmp_dir = self._make_temp_content(items)

    def _fix_entry(entry):
      return entry.clone_replace_root_dir('/tmp')

    def _fix_entries(entries):
      return bf_entry_list([ _fix_entry(entry) for entry in entries ])

    def _fix_root_dir(root_dir):
      return root_dir.replace(tmp_dir, '/tmp')
    
    def _fix_walk_item(item):
      fixed_root_dir = _fix_root_dir(item.root_dir)
      fixed_dirs = _fix_entries(item.dirs)
      fixed_files = _fix_entries(item.files)
      return bf_walk._bf_walk_item(fixed_root_dir,
                                   fixed_dirs.basenames(),
                                   fixed_files.basenames(),
                                   item.depth)

    def _fix_walk_items(items):
      result = []
      for item in items:
        fixed_item = _fix_walk_item(item)
        result.append(fixed_item)
      return result
    
    walk_items = [ x for x in bf_walk.walk(tmp_dir, **kwargs) ]
    walk_items = _fix_walk_items(walk_items)
    return self._walk_result(tmp_dir, walk_items)

  def test_walk_basic(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    self.assertEqual( [
      ( '/tmp', [ 'emptydir', 'subdir' ], [ 'emptyfile.txt', 'foo.txt' ], 0 ),
      ( '/tmp/emptydir', [], [], 1 ),
      ( '/tmp/subdir', [ 'subberdir' ], [ 'bar.txt' ], 1 ),
      ( '/tmp/subdir/subberdir', [], [ 'baz.txt' ], 2 ),
    ], self._walk(content).result )

  def test_walk_with_walk_dir_matcher(self):
    content = [
      'file foo.txt "foo.txt\n"',
      'file subdir1/bar.txt "bar.txt\n"',
      'file subdir1/subberdir1/baz.txt "baz.txt\n"',
      'file subdir2/bar2.txt "bar2.txt\n"',
      'file subdir2/subberdir2/baz2.txt "baz2.txt\n"',
      'file subdir3/bar3.txt "bar3.txt\n"',
      'file subdir3/subberdir3/baz3.txt "baz3.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ]
    matcher = bf_file_matcher()
    matcher.add_item_fnmatch('subdir2',
                             file_type = 'dir',
                             path_type = 'basename',
                             negate = True)
    matcher.add_item_fnmatch('subdir3',
                             file_type = 'dir',
                             path_type = 'basename',
                             negate = True)
    self.assertEqual( [
      ( '/tmp', [ 'emptydir', 'subdir1' ], [ 'emptyfile.txt', 'foo.txt' ], 0 ),
      ( '/tmp/emptydir', [], [], 1 ),
      ( '/tmp/subdir1', [ 'subberdir1' ], [ 'bar.txt' ], 1 ),
      ( '/tmp/subdir1/subberdir1', [], [ 'baz.txt' ], 2 ),
    ], self._walk(content, walk_dir_matcher = matcher, walk_dir_match_type = 'all').result )
    
if __name__ == '__main__':
  unit_test.main()
