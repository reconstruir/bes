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
from bes.fs.fs.fs_tester import fs_tester
from bes.fs.fs.fs_list_options import fs_list_options
from bes.git.git_unit_test import git_temp_home_func

class _fs_git_repo_tester(fs_tester):

  def __init__(self, fixture, use_lfs, items = None):
    self.config_dir = fixture.make_temp_dir(suffix = '.config.dir')
    self.repo = git_temp_repo(remote = True, content = items, debug = fixture.DEBUG, prefix = '.repo')
    fs = fs_git_repo(self.repo.address, self.config_dir, use_lfs)
    super(_fs_git_repo_tester, self).__init__(fs)

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
    tester = self._make_tester_with_items()
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
subdir/ dir None None None
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', False) )
    
  @git_temp_home_func()
  def test_list_dir_recursive(self):
    tester = self._make_tester_with_items()
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
  def test_list_dir_empty(self):
    tester = self._make_tester()
    self.assertEqual( ( '/', 'dir', None, None, None, [] ), tester.fs.list_dir('/', True) )
    
  @git_temp_home_func()
  def test_list_dir_non_existent(self):
    tester = self._make_tester()
    with self.assertRaises(fs_error) as ctx:
      tester.fs.list_dir('/foo', False)
    self.assertEqual( 'dir not found: /foo', ctx.exception.message )
      
  @git_temp_home_func()
  def test_file_info(self):
    tester = self._make_tester_with_items()
    self.assertEqual(
      ( 'foo.txt', 'file', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {}, [] ),
      tester.fs.file_info('foo.txt') )
    
  @git_temp_home_func()
  def test_file_info_dir(self):
    tester = self._make_tester_with_items()
    self.assertEqual(
      ( 'subdir', 'dir', None, None, None, [] ),
      tester.fs.file_info('subdir') )
    
  @git_temp_home_func()
  def test_remove_file(self):
    tester = self._make_tester_with_items()
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
subdir/ dir None None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
  subdir/subberdir/ dir None None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669 {}
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    tester.fs.remove_file('foo.txt')
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
subdir/ dir None None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
  subdir/subberdir/ dir None None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669 {}
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    
  @git_temp_home_func()
  def test_upload_file_new(self):
    tester = self._make_tester_with_items()
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
subdir/ dir None None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
  subdir/subberdir/ dir None None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669 {}
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    tmp_file = self.make_temp_file(content = 'this is kiwi.txt\n')
    tester.fs.upload_file('kiwi.txt', tmp_file)
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
kiwi.txt file 17 226feef5f8831b4b6c01e44d7d746018ea6de77e0def70784bf0a53d7a7d7ab4 {}
subdir/ dir None None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
  subdir/subberdir/ dir None None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669 {}
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    
  @git_temp_home_func()
  def test_upload_file_replace(self):
    tester = self._make_tester_with_items()
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
subdir/ dir None None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
  subdir/subberdir/ dir None None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669 {}
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    tmp_file = self.make_temp_file(content = 'this is the new foo.txt\n')
    tester.fs.upload_file('foo.txt', tmp_file)
    expected = '''\
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 {}
foo.txt file 24 ee190d0691f8bd34826b9892a719892eb1accc36131ef4195dd81c0dfcf5517c {}
subdir/ dir None None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
  subdir/subberdir/ dir None None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669 {}
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )

  @git_temp_home_func()
  def test_set_file_properties(self):
    tester = self._make_tester_with_items()
    self.assertEqual(
      ( 'foo.txt', 'file', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {}, [] ),
      tester.fs.file_info('foo.txt') )
    tester.fs.set_file_attributes('foo.txt', { 'p1': 'hello', 'p2': '666' })
    self.assertEqual(
      ( 'foo.txt', 'file', 7, 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35', {'p2': '666', 'p1': 'hello'}, [] ),
      tester.fs.file_info('foo.txt') )

  @git_temp_home_func()
  def test_download_file(self):
    tester = self._make_tester_with_items()
    tmp_file = self.make_temp_file()
    tester.fs.download_file('foo.txt', tmp_file)
    self.assertEqual( 'foo.txt', file_util.read(tmp_file) )

  @git_temp_home_func()
  def test_list_dir_persistent(self):
    items = [
      'file foo.txt "foo.txt"',
    ]
    r = git_temp_repo(remote = True, content = items, debug = self.DEBUG, prefix = '.repo')
    config_dir1 = self.make_temp_dir(suffix = '.config.dir')
    fs = fs_git_repo(r.address, config_dir1, False)
    t = fs_tester(fs)
    self.assertEqual( 'foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}\n',
                      t.list_dir('/', False) )
    r.add_file('bar.txt', 'bar.txt')
    r.push()
    config_dir2 = self.make_temp_dir(suffix = '.config.dir')
    fs = fs_git_repo(r.address, config_dir2, False)
    t = fs_tester(fs)
    expected = '''\
bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae {}
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 {}
'''
    self.assertEqual( expected, t.list_dir('/', False) )
    
  @classmethod
  def _make_tester(clazz, use_lfs = False, items = None):
    return _fs_git_repo_tester(clazz, use_lfs, items = items)
  
  @classmethod
  def _make_tester_with_items(clazz, use_lfs = False):
    return clazz._make_tester(items = clazz._TEST_ITEMS)
  
if __name__ == '__main__':
  unit_test.main()
