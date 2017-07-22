#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest

from bes.system import env_var as ev

class test_env_var(unittest.TestCase):

  def test_name(self):
    d = {
      'FOO': '666',
      'BAR': 'hello',
      'PATH': 'foo:bar:baz',
    }
    self.assertEqual( '666', ev(d, 'FOO').value )
    self.assertEqual( [ '666' ], ev(d, 'FOO').path )

    e = ev(d, 'FOO')
    e.value = '1000'
    self.assertEqual( '1000', ev(d, 'FOO').value )

  def test_path(self):
    d = {
      'PATH': 'foo:bar:baz',
    }
    self.assertEqual( 'foo:bar:baz', ev(d, 'PATH').value )
    self.assertEqual( [ 'foo', 'bar', 'baz' ], ev(d, 'PATH').path )

  def test_path_duplicates(self):
    d = {
      'PATH': 'foo:bar:baz:foo',
    }
    self.assertEqual( 'foo:bar:baz:foo', ev(d, 'PATH').value )
    self.assertEqual( [ 'foo', 'bar', 'baz' ], ev(d, 'PATH').path )

  def test_path_append(self):
    d = {
      'PATH': 'foo:bar:baz',
    }
    ev(d, 'PATH').append('apple')
    self.assertEqual( [ 'foo', 'bar', 'baz', 'apple' ], ev(d, 'PATH').path )

  def test_path_prepend(self):
    d = {
      'PATH': 'foo:bar:baz',
    }
    ev(d, 'PATH').prepend('apple')
    self.assertEqual( [ 'apple', 'foo', 'bar', 'baz' ], ev(d, 'PATH').path )

  def test_path_remove(self):
    d = {
      'PATH': 'foo:bar:baz',
    }
    ev(d, 'PATH').remove('bar')
    self.assertEqual( [ 'foo', 'baz' ], ev(d, 'PATH').path )

if __name__ == "__main__":
  unittest.main()
