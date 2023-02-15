#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from os import path
import os

from bes.fs.file_util import file_util
from bes.system.env_override import env_override
from bes.system.env_override_options import env_override_options
from bes.system.os_env import os_env
from bes.testing.unit_test import unit_test

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

  def test_noop(self):
    original_env = os_env.clone_current_env()
    with env_override() as _:
      pass
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_manual_override(self):
    original_env = os_env.clone_current_env()
    with env_override() as _:
      os.environ['__BES_FRUIT__'] = 'kiwi'
      os.environ['__BES_COLOR__'] = 'green'
    self.assertEqual( original_env, os_env.clone_current_env() )
    
  def test_env_add(self):
    env_add = {
      'FRUIT': 'kiwi',
      'COLOR': 'green',
    }
    original_env = os_env.clone_current_env()
    options = env_override_options(env_add = env_add)
    with env_override(options = options) as _:
      self.assertEqual( 'kiwi', os.environ['FRUIT'] )
      self.assertEqual( 'green', os.environ['COLOR'] )
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_env_override(self):
    env = {
      'INDEX': '1',
    }
    original_env = os_env.clone_current_env()
    options = env_override_options(env = env)
    with env_override(options = options) as _:
      self.assertEqual( env, dict(os.environ) )
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_env_add_and_env_override(self):
    env = {
      'INDEX': '1',
    }
    env_add = {
      'FRUIT': 'kiwi',
      'COLOR': 'green',
    }
    original_env = os_env.clone_current_env()
    options = env_override_options(env = env,
                                   env_add = env_add)
    with env_override(options = options) as _:
      self.assertEqual( self._dict_combine(env, env_add), dict(os.environ) )
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_path_append(self):
    original_env = os_env.clone_current_env()
    env = {
      'PATH': '/bin:/usr/bin',
    }
    path_append = [ '/apple/bin', '/orange/bin' ]
    options = env_override_options(env = env,
                                   path_append = path_append)
    with env_override(options = options) as _:
      self.assertEqual( { 'PATH': '/bin:/usr/bin:/apple/bin:/orange/bin' }, dict(os.environ) )
      self.assertEqual( '/bin:/usr/bin:/apple/bin:/orange/bin', os.environ['PATH'] )
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_path_prepend(self):
    original_env = os_env.clone_current_env()
    env = {
      'PATH': '/bin:/usr/bin',
    }
    path_prepend = [ '/apple/bin', '/orange/bin' ]
    options = env_override_options(env = env,
                                   path_prepend = path_prepend)
    with env_override(options = options) as _:
      self.assertEqual( { 'PATH': '/apple/bin:/orange/bin:/bin:/usr/bin' }, dict(os.environ) )
      self.assertEqual( '/apple/bin:/orange/bin:/bin:/usr/bin', os.environ['PATH'] )
    self.assertEqual( original_env, os_env.clone_current_env() )

  def test_path_append_and_prepend(self):
    original_env = os_env.clone_current_env()
    env = {
      'PATH': '/bin:/usr/bin',
    }
    path_append = [ '/brie/bin', '/cheddar/bin' ]
    path_prepend = [ '/apple/bin', '/orange/bin' ]
    options = env_override_options(env = env,
                                   path_append = path_append,
                                   path_prepend = path_prepend)
    with env_override(options = options) as _:
      self.assertEqual( { 'PATH': '/apple/bin:/orange/bin:/bin:/usr/bin:/brie/bin:/cheddar/bin' }, dict(os.environ) )
      self.assertEqual( '/apple/bin:/orange/bin:/bin:/usr/bin:/brie/bin:/cheddar/bin', os.environ['PATH'] )
    self.assertEqual( original_env, os_env.clone_current_env() )
    
if __name__ == '__main__':
  unit_test.main()
