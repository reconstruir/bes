#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework.config_file import config_file as CF
  
class test_config_file(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/lib/bes/testing/framework'
  
  def test_parse(self):
    a = CF(self.data_path('fruit/env/fruit.bescfg'))
    expected_root_dir = path.join(self.data_dir(), 'fruit')
    expected_filename = self.data_path(self.native_filename('fruit/env/fruit.bescfg'))
    expected_data = ( 'fruit', [ path.join('${root_dir}', 'bin') ], [ path.join('${root_dir}', 'lib') ], { 'water' }, [] )
    self.assertEqual( ( expected_root_dir, expected_filename, expected_data ), a )

  def test_substitute(self):
    a = CF(self.data_path('fruit/env/fruit.bescfg'))
    b = a.substitute({})
    expected_root_dir = path.join(self.data_dir(), 'fruit')
    expected_filename = self.data_path(self.native_filename('fruit/env/fruit.bescfg'))
    expected_data_a = ( 'fruit', [ path.join('${root_dir}', 'bin') ], [ path.join('${root_dir}', 'lib') ], { 'water' }, [] )
    self.assertEqual( ( expected_root_dir, expected_filename, expected_data_a ), a )
    expected_unixpath = [ path.join(expected_root_dir, 'bin') ]
    expected_pythonpath = [ path.join(expected_root_dir, 'lib') ]
    expected_data_b = ( 'fruit', expected_unixpath, expected_pythonpath, { 'water' }, [] )
    self.assertEqual( expected_root_dir, b.root_dir )
    self.assertEqual( expected_filename, b.filename )
    self.assertEqual( 'fruit', b.data.name )
    self.assertEqual( expected_pythonpath, b.data.pythonpath )

#    self.assertEqual( ( expected_root_dir, expected_filename, expected_data_b ), b )
    
if __name__ == '__main__':
  unit_test.main()
    
