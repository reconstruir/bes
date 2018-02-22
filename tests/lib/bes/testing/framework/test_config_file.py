#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.framework import config_file as CF
from bes.testing.framework import config_file_caca
  
class test_config_file(unit_test):

  __unit_test_data_dir__ = '${BES_TEST_DATA_DIR}/bes.testing/framework'
  
  def test_parse(self):
    a = CF(self.data_path('env/foo.bescfg'))
    self.assertEqual( ( self.data_dir(),
                        self.data_path('env/foo.bescfg'),
                        ( 'foo', [ '${root}/bin' ], [ '${root}/lib' ], set([ 'bar', 'baz' ]) ) ), a )

  def test_substitute(self):
    a = CF(self.data_path('env/foo.bescfg'))
    b = a.substitute({ 'root': '/tmp' })
    self.assertEqual( ( self.data_dir(),
                        self.data_path('env/foo.bescfg'),
                        ( 'foo', [ '/tmp/bin' ], [ '/tmp/lib' ], set([ 'bar', 'baz' ]) ) ), b )

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
    
