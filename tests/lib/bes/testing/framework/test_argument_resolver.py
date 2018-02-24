#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import argument_resolver as AR
  
class test_argument_resolver(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework/orange'
  
  def test_dot_dir(self):
    a = AR(self.data_dir(), [ '.' ])
    self.assertEqual( [ '.' ], a.files )
    self.assertEqual( [], a.filters )
#    self.assertEqual( [], a.resolved_files )

  def test_one_file(self):
    a = AR(self.data_dir(), [ 'tests/lib/orange/common/test_orange_util.py' ])
    self.assertEqual( [ 'tests/lib/orange/common/test_orange_util.py' ], a.files )
    self.assertEqual( [], a.filters )
    self.assertEqual( [ self.data_path('tests/lib/orange/common/test_orange_util.py') ], a.resolved_files )
    
  def test_basic(self):
    a = AR(self.data_dir(), [ '.', ':test_orange_func_one' ])
    self.assertEqual( [ '.' ], a.files )
    self.assertEqual( [ ( None, None, 'test_orange_func_one' ) ], a.filters )
#    self.assertEqual( [], a.resolved_files )
    
if __name__ == '__main__':
  unit_test.main()
    
