#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.framework import config_file_caca
  
class test_config_file_caca(unit_test):

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
    
