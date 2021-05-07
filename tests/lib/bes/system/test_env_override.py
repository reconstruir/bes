#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from os import path
from bes.testing.unit_test import unit_test
from bes.system.env_override import env_override
from bes.system.os_env import os_env
from bes.fs.file_util import file_util

class test_env_override(unit_test):

  def test_env_override_init(self):
    original_env = os_env.clone_current_env()
    with env_override( { 'FOO': '666', 'BAR': 'hi' }) as env:
      pass
    self.assertEqual( original_env, os_env.clone_current_env() )
  
  def test_env_override_set(self):
    original_env = os_env.clone_current_env()
    with env_override() as env:
      env.set('FOO', '666')
      env.set('BAR', 'hi')
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_env_override_push_pop(self):
    original_env = os_env.clone_current_env()
    with env_override() as env:
      env.push()
      env.set('FOO', '666')
      self.assertEqual( self._dict_combine(original_env, { 'FOO': '666' }), os_env.clone_current_env() )
      env.push()
      env.set('BAR', '667')
      self.assertEqual( self._dict_combine(original_env, { 'FOO': '666', 'BAR': '667' }), os_env.clone_current_env() )
      env.pop()
      self.assertEqual( self._dict_combine(original_env, { 'FOO': '666' }), os_env.clone_current_env() )
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

  def test_env_override_temp_home_enter_functions(self):

    def _setup_fruit_txt():
      file_util.save(path.expanduser('~/fruit.txt'), content = 'kiwi')
      
    with env_override.temp_home(enter_functions = [ _setup_fruit_txt ]) as env:
      self.assert_text_file_equal( 'kiwi', path.expanduser('~/fruit.txt'), strip = True )
  
if __name__ == '__main__':
  unit_test.main()
