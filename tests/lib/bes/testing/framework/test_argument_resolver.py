#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import argument_resolver as AR
  
class test_argument_resolver(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework'

  def test_config(self):
    ar = self._make_test_argument_resolver([ 'water/tests/lib/water/common/test_water_util.py' ])
    self.assertEqual( 1, len(ar.resolved_files) )
    self.assertEqual( ( self.data_path('water'), self.data_path('water/env/water.bescfg'), ( 'water', ['${root_dir}/bin'], ['${root_dir}/lib'], set() ) ),
                      ar.resolved_files[0].file_info.config )
  
  def test_dot_dir_water(self):
    ar = self._make_test_argument_resolver([ '.' ], working_dir = self.data_path('water'))
    self.assertEqual( 1, len(ar.resolved_files) )
    self.assertEqual( self.data_path('water/tests/lib/water/common/test_water_util.py'), ar.resolved_files[0].file_info.filename )
    
  def test_dot_dir_orange(self):
    ar = self._make_test_argument_resolver([ '.' ], working_dir = self.data_path('orange'))
    self.assertEqual( 1, len(ar.resolved_files) )
    self.assertEqual( self.data_path('orange/tests/lib/orange/common/test_orange_util.py'), ar.resolved_files[0].file_info.filename )
    
  def test_dot_dir(self):
    ar = self._make_test_argument_resolver([ '.' ], working_dir = self.data_dir())
    self.assertEqual( 2, len(ar.resolved_files) )
    self.assertEqual( self.data_path('orange/tests/lib/orange/common/test_orange_util.py'), ar.resolved_files[0].file_info.filename )
    self.assertEqual( self.data_path('water/tests/lib/water/common/test_water_util.py'), ar.resolved_files[1].file_info.filename )
    
  def test_filename_filter(self):
    ar = self._make_test_argument_resolver([ '.', 'test_water' ], working_dir = self.data_dir())
    self.assertEqual( 1, len(ar.resolved_files) )
    self.assertEqual( self.data_path('water/tests/lib/water/common/test_water_util.py'), ar.resolved_files[0].file_info.filename )
    
  def _make_test_argument_resolver(self, arguments, file_ignore_filename = None, working_dir = None, root_dir = None):
    working_dir = working_dir or self.data_dir()
    root_dir = root_dir or self.data_dir()
    return AR(working_dir, arguments, root_dir = root_dir, file_ignore_filename = file_ignore_filename)

if __name__ == '__main__':
  unit_test.main()
    
