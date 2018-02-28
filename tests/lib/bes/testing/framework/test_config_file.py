#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import config_file as CF
  
class test_config_file(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework'
  
  def test_parse(self):
    a = CF(self.data_path('fruit/env/fruit.bescfg'))
    self.assertEqual( ( path.join(self.data_dir(), 'fruit'),
                        self.data_path('fruit/env/fruit.bescfg'),
                        ( 'fruit', [ '${root_dir}/bin' ], [ '${root_dir}/lib' ], { 'water' } ) ), a )

  def xtest_substitute(self):
    a = CF(self.data_path('fruit/env/fruit.bescfg'))
    b = a.substitute()
    self.assertEqual( ( path.join(self.data_dir(), 'fruit'),
                        self.data_path('fruit/env/fruit.bescfg'),
                        ( 'fruit', [ path.join(self.data_dir(), 'bin') ], [ path.join(self.data_dir(), 'lib') ], { 'water' } ) ), b )
    
if __name__ == '__main__':
  unit_test.main()
    
