#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from collections import namedtuple

from bes.files.bf_entry import bf_entry
from bes.files.bf_entry_list import bf_entry_list
from bes.files.find.bf_walk import bf_walk
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
    for x in walk_items:
      print(f' BAD: {x}')
    walk_items = _fix_walk_items(walk_items)
    for x in walk_items:
      print(f'GOOD: {x}')
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

#GOOD: _bf_walk_item(root_dir='/tmp', dirs=[/tmp/emptydir, /tmp/subdir], files=[/tmp/emptyfile.txt, /tmp/foo.txt], depth=0)
#GOOD: _bf_walk_item(root_dir='/tmp/emptydir', dirs=[], files=[], depth=1)
#GOOD: _bf_walk_item(root_dir='/tmp/subdir', dirs=[/tmp/subdir/subberdir], files=[/tmp/subdir/bar.txt], depth=1)
#GOOD: _bf_walk_item(root_dir='/tmp/subdir/subberdir', dirs=[], files=[/tmp/subdir/subberdir/baz.txt], depth=2)

if __name__ == '__main__':
  unit_test.main()
