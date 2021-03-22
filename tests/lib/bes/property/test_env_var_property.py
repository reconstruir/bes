#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.system.env_override import env_override
from bes.testing.unit_test import unit_test
from bes.property.env_var_property import env_var_property
from bes.system.host import host
from bes.testing.unit_test_skip import skip_if

class test_env_var_property(unit_test):

  class fruit(object):
      
    def __init__(self, color, flavor):
      self._color = color
      self._flavor = flavor
    
    @env_var_property
    def color(self):
      return self._color
  
    @env_var_property
    def flavor(self):
      return self._flavor
  
  def test_env_var_no_var(self):
    f = self.fruit('yellow', 'tart')
    self.assertEqual( 'yellow', f.color )
    self.assertEqual( 'tart', f.flavor )
  
  def test_env_var_one_var(self):
    f = self.fruit('${COLOR}', 'tart')
    with env_override( { 'COLOR': 'yellow' }) as env:
      self.assertEqual( 'yellow', f.color )
      self.assertEqual( 'tart', f.flavor )
  
  def test_env_var_two_vars(self):
    f = self.fruit('${MODIFIER}${COLOR}', 'tart')
    with env_override( { 'COLOR': 'yellow', 'MODIFIER': 'nice' }) as env:
      self.assertEqual( 'niceyellow', f.color )
      self.assertEqual( 'tart', f.flavor )

  def test_env_var_multiple_vars(self):
    f = self.fruit('${COLOR}', '${FLAVOR}')
    with env_override( { 'COLOR': 'yellow', 'FLAVOR': 'tart' }) as env:
      self.assertEqual( 'yellow', f.color )
      self.assertEqual( 'tart', f.flavor )

  @skip_if(not host.is_unix(), 'not unix')
  def test_env_var_tilde(self):
    f = self.fruit('yellow', '~/tart')
    with env_override( { 'HOME': '/tmp/foo' }) as env:
      self.assertEqual( 'yellow', f.color )
      self.assertEqual( '/tmp/foo/tart', f.flavor )
    
  @skip_if(not host.is_unix(), 'not unix')
  def test_env_var_tilde_and_var(self):
    f = self.fruit('yellow', '~/${FLAVOR}')
    with env_override( { 'HOME': '/tmp/foo', 'FLAVOR': 'tart' }) as env:
      self.assertEqual( 'yellow', f.color )
      self.assertEqual( '/tmp/foo/tart', f.flavor )
    
if __name__ == '__main__':
  unit_test.main()
