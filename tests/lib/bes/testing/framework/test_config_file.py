#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from bes.testing.unit_test import unit_test
from bes.testing.framework import config_file as CF
from bes.testing.framework import config_file_caca
  
class test_config_file(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework'
  
  def test_parse(self):
    a = CF(self.data_path('fruit/env/fruit.bescfg'))
    self.assertEqual( ( path.join(self.data_dir(), 'fruit'),
                        self.data_path('fruit/env/fruit.bescfg'),
                        ( 'fruit', [ '${root}/bin' ], [ '${root}/lib' ], { 'water' } ) ), a )

  def test_substitute(self):
    a = CF(self.data_path('fruit/env/fruit.bescfg'))
    b = a.substitute({ 'root': '/tmp' })
    self.assertEqual( ( path.join(self.data_dir(), 'fruit'),
                        self.data_path('fruit/env/fruit.bescfg'),
                        ( 'fruit', [ '/tmp/bin' ], [ '/tmp/lib' ], { 'water' } ) ), b )

  def test_find_config_files(self):
    expected_files = [
      'citrus/env/citrus.bescfg',
      'fiber/env/fiber.bescfg',
      'fruit/env/fruit.bescfg',
      'kiwi/env/kiwi.bescfg',
      'orange/env/orange.bescfg',
      'water/env/water.bescfg'
    ]
    files = CF.find_config_files(self.data_dir())
    self.assertEqual( [ path.join(self.data_dir(), x) for x in expected_files ],
                      files )

class xtest_config_file_xcaca(unit_test):

  def test_parse(self):
    text = '''
# foo
name: foo
PATH: ${root}/bin
PYTHONPATH: ${root}/lib
requires: bar baz
'''
    
    self.assertEqual( {
      'name': 'foo',
      'PATH': [ '${root}/bin' ],
      'PYTHONPATH': [ '${root}/lib' ],
      'requires': ( 'bar', 'baz' ),
    }, config_file_caca.parse(text) )

  def test_substitute_variables(self):
    config = {
      'name': 'foo',
      'PATH': [ '${root}/bin' ],
      'PYTHONPATH': [ '${root}/lib' ],
      'requires': ( 'bar', 'baz' ),
    }
    variables = { 'root': '/home/pato' }
    self.assertEqual( {
      'name': 'foo',
      'PATH': [ '/home/pato/bin' ],
      'PYTHONPATH': [ '/home/pato/lib' ],
      'requires': ( 'bar', 'baz' ),
    }, config_file_caca.substitute_variables(config, variables) )
    
if __name__ == '__main__':
  unit_test.main()
    
