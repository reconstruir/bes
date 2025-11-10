#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.files.bf_entry import bf_entry
from bes.files.find.bf_file_finder_ops import bf_file_finder_ops
from bes.fs.testing.temp_content import temp_content
from bes.system.log import logger
from bes.system import compat
import os.path as path

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

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
    ], bf_file_finder_ops.find_dirs(tmp_dir).entries.relative_filenames(sort = True) )

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
    ], bf_file_finder_ops.find_files(tmp_dir).entries.relative_filenames(sort = True) )

  def test_find_all(self):
    content = [
      'file a.txt',
      'file subdir/b.txt',
      'dir emptydir',
    ]
    tmp_dir = self._make_temp_content(content)
    entries = bf_file_finder_ops.find(tmp_dir, file_type = None).entries
    rels = entries.relative_filenames(sort = True)
    # should contain all files and dirs
    self.assertTrue('a.txt' in rels)
    self.assertTrue(path.join('subdir', 'b.txt') in rels)
    self.assertTrue('subdir' in rels)
    self.assertTrue('emptydir' in rels)

  def test_find_in_ancestors(self):
    content = [
      'file a.txt',
      'file subdir/marker.txt',
      'file subdir/deeper/file.txt',
    ]
    tmp_dir = self._make_temp_content(content)
    start = path.join(tmp_dir, 'subdir/deeper')
    found = bf_file_finder_ops.find_in_ancestors(start, 'marker.txt')
    self.assertEqual(path.join(tmp_dir, 'subdir', 'marker.txt'), found)

  def test_find_in_ancestors_none(self):
    content = [
      'file a.txt',
      'file subdir/deeper/file.txt',
    ]
    tmp_dir = self._make_temp_content(content)
    start = path.join(tmp_dir, 'subdir/deeper')
    found = bf_file_finder_ops.find_in_ancestors(start, 'notthere.txt')
    self.assertEqual(None, found)

  @unit_test_function_skip.skip_if_not_unix()
  def test_find_unreadable(self):
    content = [
      'file a.txt',
      'file b.txt',
    ]
    tmp_dir = self._make_temp_content(content)
    e = bf_entry(path.join(tmp_dir, 'b.txt'))
    e.chmod(0o000)
    result = bf_file_finder_ops.find_unreadable(tmp_dir)
    self.assertEqual([ 'b.txt' ], result.relative_filenames(sort = True))

  def test_find_empty_dirs(self):
    content = [
      'dir d1',
      'file d2/file.txt "hi\n"',
      'dir d3/empty',
    ]
    tmp_dir = self._make_temp_content(content)
    rels = bf_file_finder_ops.find_empty_dirs(tmp_dir).relative_filenames(sort = True)
    self.assertEqual(self.native_filename_list([ 'd1', 'd3/empty' ]), rels)

  def test_remove_empty_dirs(self):
    content = [
      'dir d1',
      'file d2/file.txt "hi\n"',
      'dir d3/empty',
    ]
    tmp_dir = self._make_temp_content(content)
    removed = bf_file_finder_ops.remove_empty_dirs(tmp_dir)
    self.assertEqual( self.native_filename_list([
      'd1',
      'd3',
      'd3/empty'
    ]), removed.relative_filenames(sort = True) )

    for next_removed in removed:
      self.assertEqual( False, next_removed.exists )

if __name__ == '__main__':
  unit_test.main()
