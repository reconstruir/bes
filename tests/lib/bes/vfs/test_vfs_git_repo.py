#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.git.git_temp_repo import git_temp_repo
from bes.fs.file_util import file_util

from bes.vfs.vfs_git_repo import vfs_git_repo
from bes.vfs.vfs_error import vfs_error
from bes.vfs.vfs_tester import vfs_tester
from bes.vfs.vfs_list_options import vfs_list_options
from bes.git.git_unit_test import git_temp_home_func

class _vfs_git_repo_tester(vfs_tester):

  def __init__(self, fixture, use_lfs, items = None):
    self.config_dir = fixture.make_temp_dir(suffix = '.config.dir')
    self.repo = git_temp_repo(remote = True, content = items, debug = fixture.DEBUG, prefix = '.repo')
    fs = vfs_git_repo('<unittest>', self.repo.address, self.config_dir, use_lfs)
    super(_vfs_git_repo_tester, self).__init__(fs)

class test_vfs_git_repo(unit_test):

  _TEST_ITEMS = [
    'file foo.txt "foo.txt"',
    'file subdir/bar.txt "bar.txt"',
    'file subdir/subberdir/baz.txt "baz.txt"',
    'file emptyfile.txt',
    'dir emptydir',
  ]

  @git_temp_home_func()
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
    
  @git_temp_home_func()
  def test_list_dir_many_files_non_recursive(self):
    tester = self._make_tester_with_items()
    self.assertEqual( [
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

  @git_temp_home_func()
  def test_list_dir_many_files_recursive(self):
    tester = self._make_tester_with_items()
    self.assertEqual( [
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

  @git_temp_home_func()
  def test_list_dir_empty(self):
    tester = self._make_tester(items = [])
    self.assertEqual( [], tester.list_dir_dict('/', False, tester.OPTIONS) )
    
  @git_temp_home_func()
  def test_list_dir_empty_recursive(self):
    tester = self._make_tester()
    self.assertEqual( [], tester.fs.list_dir('/', True, tester.OPTIONS) )
    
  @git_temp_home_func()
  def test_list_dir_non_existent(self):
    tester = self._make_tester()
    with self.assertRaises(vfs_error) as ctx:
      tester.fs.list_dir('/foo', False, tester.OPTIONS)
    self.assertTrue( 'dir does not exist' in ctx.exception.message )
      
  @git_temp_home_func()
  def test_list_dir_not_a_dir(self):
    tester = self._make_tester_with_items()
    with self.assertRaises(vfs_error) as ctx:
      tester.fs.list_dir('foo.txt', False, tester.OPTIONS)
    self.assertTrue( 'not a dir' in ctx.exception.message )
      
  @git_temp_home_func()
  def test_file_info_file(self):
    tester = self._make_tester_with_items()
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
    
  @git_temp_home_func()
  def test_file_info_dir(self):
    tester = self._make_tester_with_items()
    self.assertEqual( {
      'attributes': None,
      'checksums': None,
      'filename': 'subdir',
      'ftype': 'dir',
      'modification_date': '1999-01-01 01:01:01',
      'size': None,
      'children': [],
    }, tester.file_info_dict('subdir', tester.OPTIONS) )
    
  @git_temp_home_func()
  def test_remove_file(self):
    tester = self._make_tester_with_items()
    self.assertEqual( [
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
    
  @git_temp_home_func()
  def test_upload_file_new_file(self):
    tester = self._make_tester_with_items()
    self.assertEqual( [
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')},
        'children': None,
        'filename': 'emptyfile.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 0
      },
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35')},
        'children': None,
        'filename': 'foo.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 7
      },
      {
        'attributes': None,
        'checksums': None,
        'children': [],
        'filename': 'subdir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
      }
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )
    tmp_file = self.make_temp_file(content = 'this is kiwi.txt\n')
    tester.upload_file(tmp_file, 'kiwi.txt')
    self.assertEqual( [
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')},
        'children': None,
        'filename': 'emptyfile.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 0
      },
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35')},
        'children': None,
        'filename': 'foo.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 7
      },
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 '226feef5f8831b4b6c01e44d7d746018ea6de77e0def70784bf0a53d7a7d7ab4')},
        'children': None,
        'filename': 'kiwi.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 17
      },
      {
        'attributes': None,
        'checksums': None,
        'children': [],
        'filename': 'subdir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
      }
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )
    
  @git_temp_home_func()
  def test_upload_file_replace_file(self):
    tester = self._make_tester_with_items()
    self.assertEqual( [
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')},
        'children': None,
        'filename': 'emptyfile.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 0
      },
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35')},
        'children': None,
        'filename': 'foo.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 7
      },
      {
        'attributes': None,
        'checksums': None,
        'children': [],
        'filename': 'subdir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
      }
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )
    tmp_file = self.make_temp_file(content = 'this is the new foo.txt\n')
    tester.upload_file(tmp_file, 'foo.txt')
    self.assertEqual( [
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')},
        'children': None,
        'filename': 'emptyfile.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 0
      },
      {
        'attributes': {},
        'checksums': {'sha256': ('sha256',
                                 'ee190d0691f8bd34826b9892a719892eb1accc36131ef4195dd81c0dfcf5517c')},
        'children': None,
        'filename': 'foo.txt',
        'ftype': 'file',
        'modification_date': '1999-01-01 01:01:01',
        'size': 24
      },
      {
        'attributes': None,
        'checksums': None,
        'children': [],
        'filename': 'subdir',
        'ftype': 'dir',
        'modification_date': '1999-01-01 01:01:01',
        'size': None,
      }
    ], tester.list_dir_dict('/', False, tester.OPTIONS) )

  @git_temp_home_func()
  def test_set_file_properties(self):
    tester = self._make_tester_with_items()
    self.assertEqual(
      'foo.txt file 7 sha256:ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35\n',
      tester.file_info('foo.txt', tester.OPTIONS) )
    tester.set_file_attributes('foo.txt', { 'p1': 'hello', 'p2': '666' })
    self.assertEqual(
     'foo.txt file 7 sha256:ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35 p1=hello p2=666\n',
      tester.file_info('foo.txt', tester.OPTIONS) )

  @git_temp_home_func()
  def test_download_to_file(self):
    tester = self._make_tester_with_items()
    tmp_file = self.make_temp_file()
    tester.fs.download_to_file('foo.txt', tmp_file)
    self.assertEqual( b'foo.txt', file_util.read(tmp_file) )

  @git_temp_home_func()
  def xtest_list_dir_persistent(self):
    items = [
      'file foo.txt "foo.txt"',
    ]
    r = git_temp_repo(remote = True, content = items, debug = self.DEBUG, prefix = '.repo')
    config_dir1 = self.make_temp_dir(suffix = '.config.dir')
    fs = vfs_git_repo(r.address, config_dir1, False)
    t = vfs_tester(fs)
    self.assertEqual( 'foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35\n',
                      t.list_dir('/', False, tester.OPTIONS) )
    r.add_file('bar.txt', 'bar.txt')
    r.push()
    config_dir2 = self.make_temp_dir(suffix = '.config.dir')
    fs = vfs_git_repo(r.address, config_dir2, False)
    t = vfs_tester(fs)
    expected = '''\
bar.txt file 7 08bd2d247cc7aa38b8c4b7fd20ee7edad0b593c3debce92f595c9d016da40bae
foo.txt file 7 ddab29ff2c393ee52855d21a240eb05f775df88e3ce347df759f0c4b80356c35
'''
    self.assertEqual( expected, t.list_dir('/', False, tester.OPTIONS) )
    
  @classmethod
  def _make_tester(clazz, use_lfs = False, items = None):
    return _vfs_git_repo_tester(clazz, use_lfs, items = items)
  
  @classmethod
  def _make_tester_with_items(clazz, use_lfs = False):
    return clazz._make_tester(items = clazz._TEST_ITEMS)
  
if __name__ == '__main__':
  unit_test.main()
