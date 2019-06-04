#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from os import path
from bes.testing.unit_test import unit_test
from bes.system.env_override import env_override
from bes.system.os_env import os_env

class test_env_override(unit_test):

  def test_env_override_init(self):
    original_env = os_env.clone_current_env()
    with env_override( { 'foo': '666', 'bar': 'hi' }) as env:
      pass
    self.assertEqual( original_env, os_env.clone_current_env() )
  
  def test_env_override_set(self):
    original_env = os_env.clone_current_env()
    with env_override() as env:
      env.set('foo', '666')
      env.set('bar', 'hi')
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_env_override_push_pop(self):
    original_env = os_env.clone_current_env()
    with env_override() as env:
      env.push()
      env.set('foo', '666')
      self.assertEqual( self._dict_combine(original_env, { 'foo': '666' }), os_env.clone_current_env() )
      env.push()
      env.set('bar', '667')
      self.assertEqual( self._dict_combine(original_env, { 'foo': '666', 'bar': '667' }), os_env.clone_current_env() )
      env.pop()
      self.assertEqual( self._dict_combine(original_env, { 'foo': '666' }), os_env.clone_current_env() )
      env.pop()
      self.assertEqual( original_env, os_env.clone_current_env() )
      
    self.assertEqual( original_env, os_env.clone_current_env() )

  @classmethod
  def _dict_combine(clazz, *dicts):
    result = {}
    for i, n in enumerate(dicts):
      if not isinstance(n, dict):
        raise TypeError('Argument %d is not a dict' % (i + 1))
      result.update(copy.deepcopy(n))
    return result
    
if __name__ == '__main__':
  unit_test.main()
