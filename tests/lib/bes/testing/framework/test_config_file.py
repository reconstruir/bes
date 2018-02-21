#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.framework import config_file_caca
from bes.testing.framework import config_file as CF

class test_config_file(unit_test):

  def test___init__(self):
    pass

  def test_parse(self):
    text = '''
# foo
name: foo
unixpath: ${root}/bin
pythonpath: ${root}/lib
requires: bar baz
'''
    self.assertEqual( ( 'foo', [ '${root}/bin' ], [ '${root}/lib' ], set([ 'bar', 'baz' ]) ), CF.parse(text) )
  
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
    
