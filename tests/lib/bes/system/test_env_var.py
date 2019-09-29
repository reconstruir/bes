#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.system.env_var import env_var

class test_env_var(unit_test):

  def test_name(self):
    d = {
      'FOO': '666',
      'BAR': 'hello',
      'PATH': self.xp_path('foo:bar:baz'),
    }
    self.assertEqual( '666', env_var(d, 'FOO').value )
    self.assertEqual( [ '666' ], env_var(d, 'FOO').path )

    e = env_var(d, 'FOO')
    e.value = '1000'
    self.assertEqual( '1000', env_var(d, 'FOO').value )

  def test_path(self):
    d = {
      'PATH': self.xp_path('foo:bar:baz'),
    }
    self.assertEqual( self.xp_path('foo:bar:baz'), self.xp_path(env_var(d, 'PATH').value) )
    self.assertEqual( [ 'foo', 'bar', 'baz' ], env_var(d, 'PATH').path )

  def test_path_duplicates(self):
    d = {
      'PATH': self.xp_path('foo:bar:baz:foo'),
    }
    self.assertEqual( self.xp_path('foo:bar:baz:foo'), env_var(d, 'PATH').value )
    self.assertEqual( [ 'foo', 'bar', 'baz' ], env_var(d, 'PATH').path )

  def test_path_append(self):
    d = {
      'PATH': self.xp_path('foo:bar:baz'),
    }
    env_var(d, 'PATH').append('apple')
    self.assertEqual( [ 'foo', 'bar', 'baz', 'apple' ], env_var(d, 'PATH').path )

  def test_path_prepend(self):
    d = {
      'PATH': self.xp_path('foo:bar:baz'),
    }
    env_var(d, 'PATH').prepend('apple')
    self.assertEqual( [ 'apple', 'foo', 'bar', 'baz' ], env_var(d, 'PATH').path )

  def test_path_remove(self):
    d = {
      'PATH': self.xp_path('foo:bar:baz'),
    }
    env_var(d, 'PATH').remove('bar')
    self.assertEqual( [ 'foo', 'baz' ], env_var(d, 'PATH').path )

if __name__ == "__main__":
  unit_test.main()
