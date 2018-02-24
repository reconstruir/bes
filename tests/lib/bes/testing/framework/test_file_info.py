#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import file_info as FI
from bes.fs import temp_file
from bes.git import git
  
class test_file_info(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework/orange'
  
  def test_basic(self):
    a = FI(self.data_path('lib/orange/common/orange_util.py'))
    self.assertEqual( git.root(self.data_path('lib/orange/common/orange_util.py')), a.git_root )
    self.assertEqual( True, a.git_tracked )
    
  def test_no_git_root(self):
    a = FI(temp_file.make_temp_file(content = 'def foo(): return 666\n'))
    self.assertEqual( None, a.git_root )
    self.assertEqual( False, a.git_tracked )
    
if __name__ == '__main__':
  unit_test.main()
    
