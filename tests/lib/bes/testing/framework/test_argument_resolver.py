#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import argument_resolver as AR
from bes.testing.unit_test_class_skip import unit_test_class_skip

from example_data import example_data

class test_argument_resolver(unit_test):

  @classmethod
  def setUpClass(clazz):
    unit_test_class_skip.raise_skip('broken')
  
  def test_config(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ar = self._make_test_argument_resolver([ 'water/tests/lib/water/common/test_water_util.py' ])
    self.assertEqual( 1, len(ar.test_descriptions) )
    self.assertEqual( ( path.join(tmp_dir, 'water'), path.join(tmp_dir, 'water/env/water.bescfg'), ( 'water', ['${root_dir}/bin'], ['${root_dir}/lib'], set() ) ),
                      ar.test_descriptions[0].file_info.config )
  
  def test_dot_dir_water(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ar = self._make_test_argument_resolver([ '.' ], working_dir = path.join(tmp_dir, 'water'))
    self.assertEqual( 1, len(ar.test_descriptions) )
    self.assertEqual( path.join(tmp_dir, 'water/tests/lib/water/common/test_water_util.py'), ar.test_descriptions[0].file_info.filename )
    
  def test_dot_dir_orange(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ar = self._make_test_argument_resolver([ '.' ], working_dir = path.join(tmp_dir, 'orange'))
    self.assertEqual( 1, len(ar.test_descriptions) )
    self.assertEqual( path.join(tmp_dir, 'orange/tests/lib/orange/common/test_orange_util.py'), ar.test_descriptions[0].file_info.filename )
    
  def test_dot_dir(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ar = self._make_test_argument_resolver([ '.' ], working_dir = self.data_dir())
    self.assertEqual( 2, len(ar.test_descriptions) )
    self.assertEqual( path.join(tmp_dir, 'orange/tests/lib/orange/common/test_orange_util.py'), ar.test_descriptions[0].file_info.filename )
    self.assertEqual( path.join(tmp_dir, 'water/tests/lib/water/common/test_water_util.py'), ar.test_descriptions[1].file_info.filename )
    
  def test_filename_filter(self):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    ar = self._make_test_argument_resolver([ '.', 'test_water' ], working_dir = self.data_dir())
    self.assertEqual( 1, len(ar.test_descriptions) )
    self.assertEqual( path.join(tmp_dir, 'water/tests/lib/water/common/test_water_util.py'), ar.test_descriptions[0].file_info.filename )
    
  def _make_test_argument_resolver(self, arguments, file_ignore_filename = None, working_dir = None, root_dir = None):
    tmp_dir = example_data.make_temp_content(delete = not self.DEBUG)
    working_dir = working_dir or tmp_dir
    root_dir = root_dir or tmp_dir
    return AR(working_dir, arguments, root_dir = root_dir, file_ignore_filename = file_ignore_filename)

if __name__ == '__main__':
  unit_test.main()
    
