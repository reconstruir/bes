#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os, os.path as path, tarfile

from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.tar_util import tar_util
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_skip import raise_skip_if_not_unix

class test_tar_util(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/fs/tar_util'

  @classmethod
  def setUpClass(clazz):
    raise_skip_if_not_unix()
  
  def test_copy_tree(self):
    self.maxDiff = None
    src_tmp_dir = self.make_temp_dir(suffix = '.src_dir')
    dst_tmp_dir = self.make_temp_dir(suffix = '.dst_dir')
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    tar_util.copy_tree(src_tmp_dir, dst_tmp_dir)
    
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )
    
  def test_copy_tree_and_excludes(self):
    self.maxDiff = None
    src_tmp_dir = self.make_temp_dir(suffix = '.src_dir')
    dst_tmp_dir = self.make_temp_dir(suffix = '.dst_dir')
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    tar_util.copy_tree(src_tmp_dir, dst_tmp_dir, excludes = [ 'bar.txt', 'foo.txt' ])
    
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('empty'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )

  def test_copy_tree_spaces_in_filenames(self):
    self.maxDiff = None
    src_tmp_dir = self.make_temp_dir(suffix = '.src_dir-has 2 spaces-')
    dst_tmp_dir = self.make_temp_dir(suffix = '.dst_dir-has 2 spaces-')
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    tar_util.copy_tree(src_tmp_dir, dst_tmp_dir)
    
    expected_files = [
      self.p('1'),
      self.p('1/2'),
      self.p('1/2/3'),
      self.p('1/2/3/4'),
      self.p('1/2/3/4/5'),
      self.p('1/2/3/4/5/apple.txt'),
      self.p('1/2/3/4/5/kiwi.txt'),
      self.p('bar.txt'),
      self.p('empty'),
      self.p('foo.txt'),
      self.p('kiwi_link.txt'),
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ANY)
    self.assertEqual( expected_files, actual_files )
    
if __name__ == '__main__':
  unit_test.main()
