#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.testing.temp_content import temp_content
from bes.git.git_temp_repo import git_temp_repo
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.testing.unit_test_skip import raise_skip

from bes.fs.fs.fs_git_repo import fs_git_repo
from bes.fs.fs.fs_error import fs_error
from bes.fs.fs.fs_list_options import fs_list_options
from bes.git.git_unit_test import git_temp_home_func

class _fs_git_repo_tester(object):

  def __init__(self, fixture, items = None):
    self.config_dir = fixture.make_temp_dir(suffix = '.config.dir')
    self.repo = git_temp_repo(remote = False, content = items, debug = fixture.DEBUG, prefix = '.repo')
    self.fs = fs_git_repo(self.repo.root, config_dir = self.config_dir)

  def list_dir(self, *args):
    return self._call_fs('list_dir', *args)
    
  def has_file(self, *args):
    return self._call_fs('has_file', *args)
    
  def file_info(self, *args):
    return self._call_fs('file_info', *args)

  def remove_file(self, *args):
    return self._call_fs('remove_file', *args)

  def upload_file(self, *args):
    return self._call_fs('upload_file', *args)

  def download_file(self, *args):
    return self._call_fs('download_file', *args)

  def set_file_attributes(self, *args):
    return self._call_fs('set_file_attributes', *args)
    
  def _call_fs(self, func_name, *args):
    func = getattr(self.fs, func_name)
    options = fs_list_options(show_details = True)
    return func(*args).to_string(options = options)
    
  @classmethod
  def _make_temp_content(clazz, items, debug):
    return temp_content.write_items_to_temp_dir(items, delete = debug)

class test_fs_git_repo(unit_test):

  _TEST_ITEMS = [
    'file foo.txt "foo.txt"',
    'file subdir/bar.txt "bar.txt"',
    'file subdir/subberdir/baz.txt "baz.txt"',
    'file emptyfile.txt',
    'dir emptydir',
  ]
  
  @git_temp_home_func()
  def test_list_dir(self):
    tester = self._make_tester()
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
subdir/ dir None None None
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', False) )
    
  @git_temp_home_func()
  def test_list_dir_recursive(self):
    tester = self._make_tester()
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
subdir/ dir None None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
  subdir/subberdir/ dir None None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669 {}
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    
  @git_temp_home_func()
  def xtest_list_dir_empty(self):
    tmp_dir = self.make_temp_dir()
    fs = fs_git_repo(tmp_dir)
    self.assertEqual( ( '/', 'dir', None, None, None, [] ), fs.list_dir('/', True) )
    
  @git_temp_home_func()
  def xtest_list_dir_non_existent(self):
    tmp_dir = self.make_temp_dir()
    fs = fs_git_repo(tmp_dir)
    with self.assertRaises(fs_error) as ctx:
      fs.list_dir('/foo', False)
    self.assertEqual( 'dir not found: /foo', ctx.exception.message )
      
  @git_temp_home_func()
  def test_file_info(self):
    tester = self._make_tester()
    self.assertEqual(
      ( 'foo.txt', 'file', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {}, [] ),
      tester.fs.file_info('foo.txt') )
    
  @git_temp_home_func()
  def test_file_info_dir(self):
    tester = self._make_tester()
    self.assertEqual(
      ( 'subdir', 'dir', None, None, None, [] ),
      tester.fs.file_info('subdir') )
    
  @git_temp_home_func()
  def xtest_remove_file(self):
    tester = self._make_tester()
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    tester.fs.remove_file('foo.txt')
    self.assertEqual( [
      'emptyfile.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    
  @git_temp_home_func()
  def xtest_upload_file_new(self):
    tester = self._make_tester()
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    tmp_file = self.make_temp_file(content = 'this is kiwi.txt\n')
    tester.fs.upload_file('kiwi.txt', tmp_file)
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'kiwi.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    
  @git_temp_home_func()
  def xtest_upload_file_replace(self):
    tester = self._make_tester()
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    self.assertEqual(
      ( 'foo.txt', 'file', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
      tester.fs.file_info('foo.txt') )
    tmp_file = self.make_temp_file(content = 'this is the new foo.txt\n')
    tester.fs.upload_file('foo.txt', tmp_file)
    self.assertEqual( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    self.assertEqual(
      ( 'foo.txt', 'file', 24, 'ee190d0691f8bd34826b9892a719892eb1accc36131ef4195dd81c0dfcf5517c', {} ),
      tester.fs.file_info('foo.txt') )

  @git_temp_home_func()
  def xtest_set_file_properties(self):
    tester = self._make_tester()
    self.assertEqual(
      ( 'foo.txt', 'file', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {} ),
      tester.fs.file_info('foo.txt') )
    tester.fs.set_file_attributes('foo.txt', { 'p1': 'hello', 'p2': '666' })
    self.assertEqual(
      ( 'foo.txt', 'file', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {u'p2': '666', u'p1': 'hello'} ),
      tester.fs.file_info('foo.txt') )

  @git_temp_home_func()
  def xtest_download_file(self):
    tester = self._make_tester()
    tmp_file = self.make_temp_file()
    tester.fs.download_file('foo.txt', tmp_file)
    self.assertEqual( 'foo.txt', file_util.read(tmp_file) )
    
  @classmethod
  def _make_tester(self):
    return _fs_git_repo_tester(self, items = self._TEST_ITEMS)
  
if __name__ == '__main__':
  unit_test.main()
