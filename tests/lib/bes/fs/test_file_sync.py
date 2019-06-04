#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs.file_find import file_find
from bes.fs.file_sync import file_sync
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file
from bes.fs.testing.temp_content import temp_content

class test_file_find(unit_test):

  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  def test_file_sync_basic(self):
    tmp_src_dir = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])
    tmp_dst_dir = temp_file.make_temp_dir()
    file_sync.sync(tmp_src_dir, tmp_dst_dir)
    expected = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]
    self.assertEqual( expected, file_find.find(tmp_dst_dir, relative = True) )

  def test_file_sync_remove_one(self):
    tmp_src_dir1 = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])
    tmp_src_dir2 = self._make_temp_content([
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])
    tmp_dst_dir = temp_file.make_temp_dir()
    file_sync.sync(tmp_src_dir1, tmp_dst_dir)
    file_sync.sync(tmp_src_dir2, tmp_dst_dir)
    expected = [
      'emptyfile.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]
    self.assertEqual( expected, file_find.find(tmp_dst_dir, relative = True) )

  def test_file_sync_change_one(self):
    tmp_src_dir1 = self._make_temp_content([
      'file foo.txt "first foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])
    tmp_src_dir2 = self._make_temp_content([
      'file foo.txt "second foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])
    tmp_dst_dir = temp_file.make_temp_dir()
    file_sync.sync(tmp_src_dir1, tmp_dst_dir)
    file_sync.sync(tmp_src_dir2, tmp_dst_dir)
    expected = [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ]
    self.assertEqual( expected, file_find.find(tmp_dst_dir, relative = True) )
    self.assertEqual( 'second foo.txt\n', file_util.read(path.join(tmp_dst_dir, 'foo.txt'), codec = 'utf8') )

  def test_file_sync_with_exclude(self):
    tmp_src_dir = self._make_temp_content([
      'file foo.txt "foo.txt\n"',
      'file subdir/bar.txt "bar.txt\n"',
      'file subdir/subberdir/baz.txt "baz.txt\n"',
      'file emptyfile.txt',
      'dir emptydir',
    ])
    tmp_dst_dir = temp_file.make_temp_dir()
    file_sync.sync(tmp_src_dir, tmp_dst_dir, exclude = [ 'foo.txt', 'subdir/subberdir/baz.txt' ])
    expected = [
      'emptyfile.txt',
      'subdir/bar.txt',
    ]
    self.assertEqual( expected, file_find.find(tmp_dst_dir, relative = True) )

    
if __name__ == "__main__":
  unit_test.main()
