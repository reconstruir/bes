#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import argument_resolver as AR
  
class test_argument_resolver(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework'

  def test_config(self):
    ar = self._make_test_argument_resolver([ 'water/tests/lib/water/common/test_water_util.py' ])
    self.assertEqual( 1, len(ar.files) )
    self.assertEqual( ( self.data_path('water'), self.data_path('water/env/water.bescfg'), ( 'water', ['${root}/bin'], ['${root}/lib'], set() ) ),
                      ar.files[0].file_info.config )
  
  def xtest_dot_dir(self):
    ar = self._make_test_argument_resolver([ '.' ])
#    self.assertEqual( [ '.' ], ar.files )
    self.assertEqual( [], ar.filters )
#    self.assertEqual( [], ar.resolved_files )

  def xtest_one_file(self):
    ar = self._make_test_argument_resolver([ 'tests/lib/orange/common/test_orange_util.py' ])
    self.assertEqual( [ 'tests/lib/orange/common/test_orange_util.py' ], ar.files )
    self.assertEqual( [], ar.filters )
    self.assertEqual( [ self.data_path('tests/lib/orange/common/test_orange_util.py') ], ar.files )
    
  def xtest_basic(self):
    ar = self._make_test_argument_resolver([ '.', ':test_orange_func_one' ])
#    self.assertEqual( [ '.' ], ar.files )
    self.assertEqual( [ ( None, None, 'test_orange_func_one' ) ], ar.filters )
#    self.assertEqual( [], ar.resolved_files )


#  def _make_test_argument_resolver(self, arguments, file_ignore_filename = None):
#    working_dir = self.data_dir()
#    root_dir = self.data_dir()
#    return AR(working_dir, arguments, root_dir = 

  def _make_test_argument_resolver(self, arguments, file_ignore_filename = None):
    working_dir = self.data_dir()
    root_dir = self.data_dir()
    return AR(working_dir, arguments, root_dir = root_dir, file_ignore_filename = file_ignore_filename)

if __name__ == '__main__':
  unit_test.main()
    
