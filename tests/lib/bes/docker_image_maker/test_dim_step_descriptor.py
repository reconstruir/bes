#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.testing.unit_test_class_skip import unit_test_class_skip
from bes.pyinstaller.pyinstaller import pyinstaller

_AVAILABLE=False
try:
  from bes.docker_image_maker.dim_step_descriptor import dim_step_descriptor
  from bes.docker_image_maker.dim_error import dim_error
  _AVAILABLE=True
except ImportError as ex:
  pass

class test_dim_step_descriptor(unit_test):

  @classmethod
  def setUpClass(clazz):
    if not _AVAILABLE:
      unit_test_class_skip.raise_skip('not available.')
    pyinstaller.raise_skip_if_is_binary()
  
  def test_repo_name(self):
    self.assertEqual( 'foo/bar/base', dim_step_descriptor('foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7' ).repo_name )
    
  def test_tag(self):
    self.assertEqual( '1.2.3_ubuntu-18_py2.7', dim_step_descriptor('foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7' ).tag )
    
  def test_named_tag(self):
    self.assertEqual( 'foo/bar/base:1.2.3_ubuntu-18_py2.7', dim_step_descriptor('foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7' ).named_tag )

  def test_named_tag_with_address(self):
    self.assertEqual( 'foo/bar/base:1.2.3_ubuntu-18_py2.7',
                      dim_step_descriptor('foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7', address = '666.foo.example.com' ).named_tag )
    
  def test_addressed_named_tag(self):
    self.assertEqual( '666.foo.example.com/foo/bar/base:1.2.3_ubuntu-18_py2.7',
                      dim_step_descriptor('foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7', address = '666.foo.example.com' ).addressed_named_tag )    
    
  def test_parse(self):
    self.assertEqual( ( 'foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7', None ),
                      dim_step_descriptor.parse('foo/bar/base:1.2.3_ubuntu-18_py2.7') )

  def test_parse_has_address(self):
    self.assertEqual( ( 'foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7', '666.foo.example.com' ),
                      dim_step_descriptor.parse('666.foo.example.com/foo/bar/base:1.2.3_ubuntu-18_py2.7', has_address = True) )

  def test_addressed_repo_name_no_address(self):
    with self.assertRaises(dim_error) as ctx:
      dim_step_descriptor('foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7' ).addressed_repo_name

  def test_addressed_repo_name_no_address(self):
    self.assertEqual( '666.foo.example.com/foo/bar/base',
                      dim_step_descriptor('foo/bar', 'base', '1.2.3', 'ubuntu', '18', '2.7', address = '666.foo.example.com' ).addressed_repo_name )

    
if __name__ == '__main__':
  unit_test.main()
