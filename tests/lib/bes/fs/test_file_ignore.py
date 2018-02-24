#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.fs import file_ignore as FI, temp_file
  
class test_file_ignore(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.fs/file_ignore'
  
  def test_basic(self):
    pass
  
if __name__ == '__main__':
  unit_test.main()
    
