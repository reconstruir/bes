#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, pprint, sys
from os import path
from datetime import datetime

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test
from bes.vfs.vfs_error import vfs_error
from bes.vfs.vfs_file_info_options import vfs_file_info_options
from bes.vfs.vfs_local import vfs_local
from bes.vfs.vfs_tester import vfs_tester

class _vfs_local_tester(vfs_tester):

  def __init__(self, fixture, items = None):
    self.local_root_dir = temp_content.write_items_to_temp_dir(items, delete = not fixture.DEBUG)
    fs = vfs_local('<unittest>', self.local_root_dir)
    super(_vfs_local_tester, self).__init__(fs)

class test_vfs_local(unit_test):
  
  _TEST_ITEMS = [
    'file foo.txt "foo.txt"',
    'file subdir/bar.txt "bar.txt"',
    'file subdir/subberdir/baz.txt "baz.txt"',
    'file emptyfile.txt',
    'dir emptydir',
  ]

  def test_list_dir_empty(self):
    tester = self._make_tester(items = [])
    self.assertEqual( [], tester.list_dir_dict('/', False, tester.OPTIONS) )
  
  def test_list_dir_one_file(self):
    items = [
      'file foo.txt "foo.txt"',
    ]
    tester = self._make_tester(items = items)
    self.assertEqual( [
      {
        'modification_date': '1999-01-01 01:01:01',
        'filename': 'foo.txt',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35' ) },
        'size': 7,
        'children': None,
      },
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )
    
  def test_list_dir_many_files_non_recursive(self):
    tester = self._make_tester()
    self.assertEqual( [
      {
        'attributes': None,
        'checksums': None,
        'filename': 'emptydir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [],
      },
      {
        'modification_date': '1999-01-01 01:01:01',
        'filename': 'emptyfile.txt',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' ) },
        'size': 0,
        'children': None,
      },
      {
        'modification_date': '1999-01-01 01:01:01',
        'filename': 'foo.txt',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35' ) },
        'size': 7,
        'children': None,
      },
      {
        'attributes': None,
        'checksums': None,
        'filename': 'subdir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [],
      },
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )

  def test_list_dir_many_files_recursive(self):
    tester = self._make_tester()
    self.assertEqual( [
      {
        'filename': 'emptydir', 
        'attributes': None,
        'checksums': None,
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [],
      },
      {
        'filename': 'emptyfile.txt',
        'modification_date': '1999-01-01 01:01:01',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' ) },
        'size': 0,
        'children': None,
      },
      {
        'filename': 'foo.txt',
        'modification_date': '1999-01-01 01:01:01',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35' ) },
        'size': 7,
        'children': None,
      },
      {
        'filename': 'subdir',
        'attributes': None,
        'checksums': None,
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [
          {
            'filename': 'subdir/bar.txt',
            'attributes': {},
            'checksums': { 'sha256': ( 'sha256', '08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae' ) },
            'children': None,
            'ftype': 'file',
            'modification_date': '1999-01-01 01:01:01',
            'size': 7,
          },
          {
            'filename': 'subdir/subberdir',
            'ftype': 'dir',
            'modification_date': '1999-01-01 01:01:01',
            'size': None,
            'attributes': None,
            'checksums': None,
            'children': [
              {
                'filename': 'subdir/subberdir/baz.txt',
                'attributes': {},
                'checksums': {
                  'sha256': ( 'sha256', '541ea9c9d29b720d2b1c4d661e983865e2cd0943ca00ccf5d08319d0dcfff669' )
                },
                'children': None,
                'ftype': 'file',
                'modification_date': '1999-01-01 01:01:01',
                'size': 7,
              },
            ],
          },
        ],
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
      },
    ], tester.list_dir_dict('/', True, tester.OPTIONS) )
    
  def test_list_dir_empty(self):
    tmp_dir = self.make_temp_dir()
    fs = vfs_local('<unittest>', tmp_dir)
    self.assertEqual( [], fs.list_dir('/', True, vfs_tester.OPTIONS) )
    
  def test_list_dir_non_existent(self):
    tmp_dir = self.make_temp_dir()
    fs = vfs_local('<unittest>', tmp_dir)
    with self.assertRaises(vfs_error) as ctx:
      fs.list_dir('/notthere', False, vfs_tester.OPTIONS)
    self.assertTrue( 'dir does not exist' in ctx.exception.message )

  def test_file_info_root(self):
    tester = self._make_tester()
    self.assertEqual( {
      'attributes': None,
      'checksums': None,
      'filename': '/',
      'ftype': 'dir',
      'modification_date': '1999-01-01 01:01:01',
      'size': None,
      'children': [],
    }, tester.file_info_dict('/', tester.OPTIONS) )
    
  def test_file_info_file(self):
    tester = self._make_tester()
    self.assertEqual( {
      'attributes': {},
      'checksums': {
        'sha256': ( 'sha256', 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35' ),
      },
      'filename': 'foo.txt',
      'ftype': 'file',
      'modification_date': '1999-01-01 01:01:01',
      'size': 7,
      'children': None,
    }, tester.file_info_dict('foo.txt', tester.OPTIONS) )
    
  def test_file_info_dir(self):
    tester = self._make_tester()
    self.assertEqual( {
      'attributes': None,
      'checksums': None,
      'filename': 'subdir',
      'ftype': 'dir',
      'modification_date': '1999-01-01 01:01:01',
      'size': None,
      'children': [],
    }, tester.file_info_dict('subdir', tester.OPTIONS) )
    
  def test_remove_file(self):
    tester = self._make_tester()
    self.assertEqual( [
      {
        'attributes': None,
        'checksums': None,
        'filename': 'emptydir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [],
      },
      {
        'modification_date': '1999-01-01 01:01:01',
        'filename': 'emptyfile.txt',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' ) },
        'size': 0,
        'children': None,
      },
      {
        'modification_date': '1999-01-01 01:01:01',
        'filename': 'foo.txt',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35' ) },
        'size': 7,
        'children': None,
      },
      {
        'attributes': None,
        'checksums': None,
        'filename': 'subdir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [],
      },
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )
    tester.remove_file('foo.txt')
    self.assertEqual( [
      {
        'attributes': None,
        'checksums': None,
        'filename': 'emptydir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [],
      },
      {
        'modification_date': '1999-01-01 01:01:01',
        'filename': 'emptyfile.txt',
        'ftype': 'file',
        'attributes': {},
        'checksums': { 'sha256': ( 'sha256', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855' ) },
        'size': 0,
        'children': None,
      },
      {
        'attributes': None,
        'checksums': None,
        'filename': 'subdir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
        'children': [],
      },
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )

  def test_upload_file_new_file(self):
    tester = self._make_tester()
    self.assert_path_list_equal( [
      'emptyfile.txt',
      'foo.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    tmp_file = self.make_temp_file(content = 'this is kiwi.txt')
    tester.upload_file(tmp_file, 'kiwi.txt')
    self.assert_path_list_equal( [
      'emptyfile.txt',
      'foo.txt',
      'kiwi.txt',
      'subdir/bar.txt',
      'subdir/subberdir/baz.txt',
    ], file_find.find(tester.local_root_dir) )
    
  def xtest_upload_file_replace_file(self):
    tester = self._make_tester()
    self.assertEqual( {
      'attributes': {},
      'checksums': {
        'sha256': ( 'sha256', 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35' ),
      },
      'filename': 'foo.txt',
      'ftype': 'file',
      'modification_date': '1999-01-01 01:01:01',
      'size': 7,
      'children': None,
    }, tester.file_info_dict('foo.txt', tester.OPTIONS) )
    tmp_file = self.make_temp_file(content = 'this is the new foo.txt')
    tester.upload_file(tmp_file, 'foo.txt')
    self.assertEqual( {
      'attributes': {},
      'checksums': {
        'sha256': ( 'sha256', '85a746121aaabbdab676f911f30c712873e053c6920af1132834e1bbdfc14bb5' ),
      },
      'filename': 'foo.txt',
      'ftype': 'file',
      'modification_date': '1999-01-01 01:01:01',
      'size': 23,
      'children': None,
    }, tester.file_info_dict('foo.txt', tester.OPTIONS) )

  def test_set_file_properties(self):
    tester = self._make_tester()
    self.assertEqual(
      'foo.txt file 7 sha256:ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35\n',
      tester.file_info('foo.txt', tester.OPTIONS) )
    tester.set_file_attributes('foo.txt', { 'p1': 'hello', 'p2': '666' })
    self.assertEqual(
     'foo.txt file 7 sha256:ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 p1=hello p2=666\n',
      tester.file_info('foo.txt', tester.OPTIONS) )

  def test_download_to_file(self):
    tester = self._make_tester()
    tmp_file = self.make_temp_file()
    tester.download_to_file('foo.txt', tmp_file)
    self.assertEqual( b'foo.txt', file_util.read(tmp_file) )
    
  def test_download_to_bytes(self):
    tester = self._make_tester()
    tmp_file = self.make_temp_file(content = 'this is foo.txt')
    tester.upload_file(tmp_file, 'x/y/z/foo.txt')
    self.assertEqual( b'this is foo.txt', tester.download_to_bytes('x/y/z/foo.txt') )
    
  @classmethod
  def _make_tester(self, items = None):
    return _vfs_local_tester(self, items = items or self._TEST_ITEMS)
  
if __name__ == '__main__':
  unit_test.main()
