#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.framework.config_data import config_data as CD

class test_config_data(unit_test):

  def test___init__(self):
    pass

  def test_parse(self):
    text = '''
# foo
name: foo
variables: v1 v2
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires: bar baz
'''
    self.assertEqual( ( 'foo', [ self.native_filename('${root_dir}/bin') ], [ self.native_filename('${root_dir}/lib') ], set([ 'bar', 'baz' ]), [ 'v1', 'v2' ] ),
                      CD.parse(text) )

  def test_substitute(self):
    text = '''
# foo
name: foo
variables: v1 v2
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires: bar baz
'''
    a = CD.parse(text)
    b = a.substitute({ 'root_dir': self.native_filename('/tmp') })
    self.assertEqual( ( 'foo', [ self.native_filename('${root_dir}/bin') ], [ self.native_filename('${root_dir}/lib') ], set([ 'bar', 'baz' ]), [ 'v1', 'v2' ] ), a )
    self.assertEqual( ( 'foo', [ self.native_filename('/tmp/bin') ], [ self.native_filename('/tmp/lib') ], set([ 'bar', 'baz' ]), [ 'v1', 'v2' ] ), b )
    
if __name__ == '__main__':
  unit_test.main()
    
