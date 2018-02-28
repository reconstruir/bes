#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.framework import config_data as CD

class test_config_data(unit_test):

  def test___init__(self):
    pass

  def test_parse(self):
    text = '''
# foo
name: foo
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires: bar baz
'''
    self.assertEqual( ( 'foo', [ '${root_dir}/bin' ], [ '${root_dir}/lib' ], set([ 'bar', 'baz' ]) ), CD.parse(text) )

  def test_substitute(self):
    text = '''
# foo
name: foo
unixpath: ${root_dir}/bin
pythonpath: ${root_dir}/lib
requires: bar baz
'''
    a = CD.parse(text)
    b = a.substitute({ 'root_dir': '/tmp' })
    self.assertEqual( ( 'foo', [ '${root_dir}/bin' ], [ '${root_dir}/lib' ], set([ 'bar', 'baz' ]) ), a )
    self.assertEqual( ( 'foo', [ '/tmp/bin' ], [ '/tmp/lib' ], set([ 'bar', 'baz' ]) ), b )
    
if __name__ == '__main__':
  unit_test.main()
    
