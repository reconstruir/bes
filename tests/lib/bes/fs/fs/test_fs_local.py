#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.testing.temp_content import temp_content
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find

from bes.fs.fs.fs_local import fs_local

class test_fs_local(unit_test):

  _TEST_ITEMS = [
    'file foo.txt "foo.txt\n"',
    'file subdir/bar.txt "bar.txt\n"',
    'file subdir/subberdir/baz.txt "baz.txt\n"',
    'file emptyfile.txt',
    'dir emptydir',
  ]
  
  def test_list_dir(self):
    fs = self._make_temp_fs()
    self.assertEqual( [
      ( 'emptyfile.txt', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', {} ),
      ( 'foo.txt', 8, 'b6a5ff9795209b3d64cb5c04d574515413f9fec7abde49d66b44de90d1e0db14', {} ),
    ], fs.list_dir('/', False) )
    
  def test_list_dir_empty(self):
    tmp_dir = self.make_temp_dir()
    fs = fs_local(tmp_dir)
    self.assertEqual( [], fs.list_dir('/', False) )
    
  def test_list_dir_non_existent(self):
    tmp_dir = self.make_temp_dir()
    file_util.remove(tmp_dir)
    fs = fs_local(tmp_dir)
    self.assertEqual( [], fs.list_dir('/', False) )

  def test_file_info(self):
    fs = self._make_temp_fs()
    self.assertEqual(
      ( 'foo.txt', 8, 'b6a5ff9795209b3d64cb5c04d574515413f9fec7abde49d66b44de90d1e0db14', {} ),
      fs.file_info('foo.txt') )
    
  def test_file_info(self):
    fs = self._make_temp_fs()
    self.assertEqual(
      ( 'foo.txt', 8, 'b6a5ff9795209b3d64cb5c04d574515413f9fec7abde49d66b44de90d1e0db14', {} ),
      fs.file_info('foo.txt') )
    
  def test_remove_file(self):
    fs = self._make_temp_fs()
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(fs._where) )
    fs.remove_file('foo.txt')
    self.assertEqual( [
      'emptyfile.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(fs._where) )
    
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  @classmethod
  def _make_temp_fs(self):
    tmp_dir = self._make_temp_content(self._TEST_ITEMS)
    return fs_local(tmp_dir)
  
if __name__ == '__main__':
  unit_test.main()
