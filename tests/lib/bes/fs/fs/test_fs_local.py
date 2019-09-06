#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, pprint, sys
from os import path

from bes.testing.unit_test import unit_test
from bes.fs.testing.temp_content import temp_content
from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.testing.unit_test_skip import raise_skip
from bes.fs.fs.fs_tester import fs_tester

from bes.fs.fs.fs_local import fs_local
from bes.fs.fs.fs_error import fs_error

class _fs_local_tester(fs_tester):

  def __init__(self, fixture, items = None):
    self.local_root_dir = self._make_temp_content(items, fixture.DEBUG)
    fs = fs_local('<unittest>', self.local_root_dir)
    super(_fs_local_tester, self).__init__(fs)

  @classmethod
  def _make_temp_content(clazz, items, debug):
    return temp_content.write_items_to_temp_dir(items, delete = debug)
    
class test_fs_local(unit_test):

  @classmethod
  def setUpClass(clazz):
    #raise_skip('work in progress not ready')
    pass
  
  _TEST_ITEMS = [
    'file foo.txt "foo.txt"',
    'file subdir/bar.txt "bar.txt"',
    'file subdir/subberdir/baz.txt "baz.txt"',
    'file emptyfile.txt',
    'dir emptydir',
  ]
  
  def test_list_dir(self):
    tester = self._make_tester()
    expected = '''\
emptydir/ dir None None
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35
subdir/ dir None None
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', False) )
    
  def test_list_dir_recursive(self):
    tester = self._make_tester()
    expected = '''\
emptydir/ dir None None
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35
subdir/ dir None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae
  subdir/subberdir/ dir None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    
  def test_list_dir_empty(self):
    tmp_dir = self.make_temp_dir()
    fs = fs_local('<unittest>',tmp_dir)
    self.assertEqual( ( '/', 'dir', None, None, None, [] ), fs.list_dir('/', True) )
    
  def test_list_dir_non_existent(self):
    tmp_dir = self.make_temp_dir()
    fs = fs_local('<unittest>',tmp_dir)
    with self.assertRaises(fs_error) as ctx:
      fs.list_dir('/foo', False)
    self.assertEqual( 'dir not found: /foo', ctx.exception.message )
      
  def test_file_info(self):
    tester = self._make_tester()
    self.assertEqual(
      'foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35\n',
      tester.file_info('foo.txt') )
    
  def test_file_info_dir(self):
    tester = self._make_tester()
    self.assertEqual(
      ( 'subdir', 'dir', None, None, None, [] ),
      tester.fs.file_info('subdir') )
    
  def test_remove_file(self):
    tester = self._make_tester()
    expected = '''\
emptydir/ dir None None
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35
subdir/ dir None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae
  subdir/subberdir/ dir None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    tester.remove_file('foo.txt')
    expected = '''\
emptydir/ dir None None
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
subdir/ dir None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae
  subdir/subberdir/ dir None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )

  def test_upload_file_new(self):
    tester = self._make_tester()
    self.assertEqual( [
      '.besfs/checksum.db/.bes_file_metadata.db',
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    tmp_file = self.make_temp_file(content = 'this is kiwi.txt\n')
    tester.upload_file(tmp_file, 'kiwi.txt')
    self.assertEqual( [
      '.besfs/checksum.db/.bes_file_metadata.db',
      'emptyfile.txt',
      'foo.txt',
      'kiwi.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    
  def test_upload_file_replace(self):
    tester = self._make_tester()
    expected = '''\
emptydir/ dir None None
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35
subdir/ dir None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae
  subdir/subberdir/ dir None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )
    tmp_file = self.make_temp_file(content = 'this is the new foo.txt\n')
    tester.upload_file(tmp_file, 'foo.txt')
    expected = '''\
emptydir/ dir None None
emptyfile.txt file 0 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
foo.txt file 24 ee190d0691f8bd34826b9892a719892eb1accc36131ef4195dd81c0dfcf5517c
subdir/ dir None None
  subdir/bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae
  subdir/subberdir/ dir None None
    subdir/subberdir/baz.txt file 7 541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669
'''
    self.assertMultiLineEqual( expected, tester.list_dir('/', True) )

  def test_set_file_properties(self):
    tester = self._make_tester()
    self.assertEqual(
      'foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35\n',
      tester.file_info('foo.txt') )
    tester.set_file_attributes('foo.txt', { 'p1': 'hello', 'p2': '666' })
    self.assertEqual(
     'foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 p1=hello p2=666\n',
      tester.file_info('foo.txt') )

  def test_download_file(self):
    tester = self._make_tester()
    tmp_file = self.make_temp_file()
    tester.download_file('foo.txt', tmp_file)
    self.assertEqual( 'foo.txt', file_util.read(tmp_file) )
    
  @classmethod
  def _make_tester(self):
    return _fs_local_tester(self, items = self._TEST_ITEMS)
  
if __name__ == '__main__':
  unit_test.main()
