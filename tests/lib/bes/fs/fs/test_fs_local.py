#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.testing.temp_content import temp_content
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.testing.unit_test_skip import raise_skip

from bes.fs.fs.fs_local import fs_local

class test_fs_local(unit_test):

  @classmethod
  def setUpClass(clazz):
    raise_skip('work in progress not ready')
  
  _TEST_ITEMS = [
    'file foo.txt "foo.txt"',
    'file subdir/bar.txt "bar.txt"',
    'file subdir/subberdir/baz.txt "baz.txt"',
    'file emptyfile.txt',
    'dir emptydir',
  ]
  
  def test_list_dir(self):
    fs = self._make_temp_fs()
    self.assertEqual( [
      ( 'emptyfile.txt', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', {} ),
      ( 'foo.txt', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
    ], fs.list_dir('/', False) )
    
  def test_list_dir_recursive(self):
    fs = self._make_temp_fs()
    self.assertEqual( [
      ( 'emptyfile.txt', 0, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', {} ),
      ( 'foo.txt', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
      ( 'subdir/bar.txt', 7, '08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae', {} ),
      ( 'subdir/subberdir/baz.txt', 7, '541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669', {} ),
    ], fs.list_dir('/', True) )
    
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
      ( 'foo.txt', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
      fs.file_info('foo.txt') )
    
  def test_file_info(self):
    fs = self._make_temp_fs()
    self.assertEqual(
      ( 'foo.txt', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
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
    
  def test_upload_file_new(self):
    fs = self._make_temp_fs()
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(fs._where) )
    tmp_file = self.make_temp_file(content = 'this is kiwi.txt\n')
    fs.upload_file('kiwi.txt', tmp_file)
    if False: self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'kiwi.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(fs._where) )
    
  def test_upload_file_replace(self):
    fs = self._make_temp_fs()
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(fs._where) )
    self.assertEqual(
      ( 'foo.txt', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
      fs.file_info('foo.txt') )
    tmp_file = self.make_temp_file(content = 'this is the new foo.txt\n')
    fs.upload_file('foo.txt', tmp_file)
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(fs._where) )
    self.assertEqual(
      ( 'foo.txt', 24, 'ee190d0691f8bd34826b9892a719892eb1accc36131ef4195dd81c0dfcf5517c', {} ),
      fs.file_info('foo.txt') )

  def test_set_file_properties(self):
    fs = self._make_temp_fs()
    self.assertEqual(
      ( 'foo.txt', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
      fs.file_info('foo.txt') )
    fs.set_file_attributes('foo.txt', { 'p1': 'hello', 'p2': '666' })
    self.assertEqual(
      ( 'foo.txt', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {u'p2': '666', u'p1': 'hello'} ),
      fs.file_info('foo.txt') )
    
  @classmethod
  def _make_temp_content(clazz, items):
    return temp_content.write_items_to_temp_dir(items, delete = not clazz.DEBUG)

  @classmethod
  def _make_temp_fs(self):
    tmp_cache_dir = self.make_temp_dir(suffix = '.cache')
    tmp_dir = self._make_temp_content(self._TEST_ITEMS)
    return fs_local(tmp_dir, cache_dir = tmp_cache_dir)
  
if __name__ == '__main__':
  unit_test.main()
