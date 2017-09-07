#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os, os.path as path, tarfile
from bes.test import unit_test
from bes.fs import file_find, file_util, tar_util, temp_file

class test_tar_util(unit_test):

  __unit_test_data_dir__ = 'test_data/tar_util'

  DEBUG = False
  #DEBUG = True

  def test_copy_tree_with_tar(self):
    self.maxDiff = None
    src_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    dst_tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    with tarfile.open(self.data_path('test.tar'), mode = 'r') as f:
      f.extractall(path = src_tmp_dir)
    tar_util.copy_tree_with_tar(src_tmp_dir, dst_tmp_dir)
    
    expected_files = [
      '1',
      '1/2',
      '1/2/3',
      '1/2/3/4',
      '1/2/3/4/5',
      '1/2/3/4/5/apple.txt',
      '1/2/3/4/5/kiwi.txt',
      'bar.txt',
      'empty',
      'foo.txt',
      'kiwi_link.txt',
    ]
    actual_files = file_find.find(dst_tmp_dir, file_type = file_find.ALL)
    self.assertEqual( expected_files, actual_files )
    
if __name__ == '__main__':
  unit_test.main()
