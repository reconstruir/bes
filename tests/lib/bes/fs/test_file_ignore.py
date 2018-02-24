#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import file_ignore FI
from bes.fs import temp_file
  
class test_file_ignore(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework/file_ignore'
  
  def test_basic(self):
    ce = config_env(self.data_dir())
    a = FI(ce, self.data_path('orange/lib/orange/common/orange_util.py'))
    self.assertEqual( git.root(self.data_path('orange/lib/orange/common/orange_util.py')), a.git_root )
    self.assertEqual( True, a.git_tracked )
    self.assertEqual( ce.config_for_name('orange'), a.config )
    
  def test_no_git_root(self):
    ce = config_env(self.data_dir())
    a = FI(ce, temp_file.make_temp_file(content = 'def foo(): return 666\n'))
    self.assertEqual( None, a.git_root )
    self.assertEqual( False, a.git_tracked )
    self.assertEqual( None, a.config )
    
if __name__ == '__main__':
  unit_test.main()
    
