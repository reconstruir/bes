#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
import os, unittest

from bes.testing.unit_test import unit_test
from bes.system.host import host
from bes.system.os_env import os_env

class test_os_env(unit_test):

  def test_path_reset(self):
    os_env.path_reset()
    self.assertTrue( os_env.CLEAN_PATH_MAP[host.SYSTEM], os_env.PATH.path )

  def test_path_append_remove(self):
    os_env.PATH.cleanup()
    old_path = os_env.PATH.path
    os_env.PATH.append('FOO')
    os_env.PATH.remove('FOO')
    self.assertEqual( old_path, os_env.PATH.path )

  def test_key_is_path(self):
    self.assertTrue( os_env.key_is_path('PATH') )
    self.assertTrue( os_env.key_is_path('LD_LIBRARY_PATH') )
    self.assertFalse( os_env.key_is_path('USER') )

  def test_update_empty(self):
    env = {}
    d = { 'PATH': self.native_path('foo:bar') }
    self.assertEqual( { 'PATH': self.native_path('foo:bar') }, os_env.clone_and_update(env, d) )
    self.assertEqual( { 'PATH': self.native_path('foo:bar') }, os_env.clone_and_update(env, d, prepend = True) )

    self.assertEqual( {}, os_env.clone_and_update({}, {}) )

  def test_update(self):
    env = { 'PATH': self.native_path('baz:biz'), 'USER': 'me' }
    d = { 'PATH': self.native_path('foo:bar') }
    self.assertEqual( { 'PATH': self.native_path('baz:biz:foo:bar'), 'USER': 'me' }, os_env.clone_and_update(env, d) )
    self.assertEqual( { 'PATH': self.native_path('foo:bar:baz:biz'), 'USER': 'me' }, os_env.clone_and_update(env, d, prepend = True) )

  def test_clone_and_update(self):
    env = { 'FOO': 666, 'BAR': 'hi' }
    d = { 'FRUIT': 'apple' }
    new_env = os_env.clone_and_update(env, d)
    self.assertEqual( { 'FOO': 666, 'BAR': 'hi', 'FRUIT': 'apple' }, new_env )
    
if __name__ == "__main__":
  unit_test.main()
