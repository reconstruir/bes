#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework.file_finder import file_finder as FF

from example_data import example_data

class test_file_finder(unit_test):

  def xtest_find_python_files(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    expected = [
      self.native_filename('lib/orange/common/__init__.py'),
      self.native_filename('lib/orange/common/orange_util.py'),
      self.native_filename('tests/lib/orange/common/test_orange_util.py'),
    ]
    self.assertEqual( [ path.join(tmp_dir, f) for f in expected ], FF.find_python_files(tmp_dir) )
    
  def xtest_find_tests(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    expected = [
      self.native_filename('tests/lib/orange/common/test_orange_util.py'),
    ]
    self.assertEqual( [ path.join(tmp_dir, f) for f in expected ], FF.find_tests(tmp_dir) )
    
if __name__ == '__main__':
  unit_test.main()
    
