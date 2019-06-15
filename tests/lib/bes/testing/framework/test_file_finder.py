#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework.file_finder import file_finder as FF
  
class test_file_finder(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework/orange'
  
  def xtest_find_python_files(self):
    expected = [
      self.p('lib/orange/common/__init__.py'),
      self.p('lib/orange/common/orange_util.py'),
      self.p('tests/lib/orange/common/test_orange_util.py'),
    ]
    self.assertEqual( [ path.join(self.data_dir(), f) for f in expected ], FF.find_python_files(self.data_dir()) )
    
  def xtest_find_tests(self):
    expected = [
      self.p('tests/lib/orange/common/test_orange_util.py'),
    ]
    self.assertEqual( [ path.join(self.data_dir(), f) for f in expected ], FF.find_tests(self.data_dir()) )
    
if __name__ == '__main__':
  unit_test.main()
    
