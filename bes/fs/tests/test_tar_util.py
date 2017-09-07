#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

import os, os.path as path
from bes.test import unit_test
from bes.fs import file_find, file_util, tar_util, temp_file

class test_tar_util(unit_test):

  __unit_test_data_dir__ = 'test_data/tar_util'

  DEBUG = False
  #DEBUG = True

  def test_copy_tree_with_tar(self):
    self.maxDiff = True
    tmp_dir = temp_file.make_temp_dir(delete = not self.DEBUG)
    tar_util.copy_tree_with_tar(self.data_dir(), tmp_dir)
    
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
    actual_files = file_find.find(tmp_dir, file_type = file_find.ALL)
    for a in actual_files:
      print "A: ", a
    self.assertEqual( expected_files, actual_files )
    
if __name__ == '__main__':
  unit_test.main()
