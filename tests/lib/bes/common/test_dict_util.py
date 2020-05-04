#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common.dict_util import dict_util
from bes.system.compat import compat

class test_dict_util(unittest.TestCase):

  def test_combine(self):
    a = { 'fruit': 'apple', 'num': 666 }
    b = { 'flavor': 'vanilla', 'greeting': 'hi' }
    c = { 'score': 5 }
    r = dict_util.combine(a, b, c)
    self.assertEqual( { 'fruit': 'apple', 'num': 666, 'flavor': 'vanilla', 'greeting': 'hi', 'score': 5 }, r )

  def test_combine_empty(self):
    a = {}
    b = { 'flavor': 'vanilla', 'greeting': 'hi' }
    r = dict_util.combine(a, b)
    self.assertEqual( { 'flavor': 'vanilla', 'greeting': 'hi' }, r )

  def test_is_homogeneous(self):
    self.assertTrue( dict_util.is_homogeneous({ 'a': '5', 'b': 'hi' }, compat.STRING_TYPES, compat.STRING_TYPES) )
    self.assertFalse( dict_util.is_homogeneous({ 'a': 5, 'b': 'hi' }, compat.STRING_TYPES, compat.STRING_TYPES) )
    self.assertFalse( dict_util.is_homogeneous({ 5: '5', 'b': 'hi' }, compat.STRING_TYPES, compat.STRING_TYPES) )

  def test_dumps(self):
    self.assertEqual( '', dict_util.dumps({}) )

  def test_dumps(self):
    self.assertEqual( 'a: 5\nb: 6\n', dict_util.dumps({ 'a': 5, 'b': 6 }) )

  def test_replace_values(self):
    d = { 'foo': '@FOO@', 'bar': '@BAR@' }
    r = { '@FOO@': 'hi', '@BAR@': 'bye' }
    dict_util.replace_values(d, r)
    self.assertEqual( { 'foo': 'hi', 'bar': 'bye' }, d )

  def test_partition_by_function(self):
    func = lambda key: key.startswith('f')
    self.assertEqual( ( {}, {} ), dict_util.partition_by_function({}, func) )
    self.assertEqual( ( { 'foo': 'hi' }, { 'bar': '666' } ), dict_util.partition_by_function({ 'foo': 'hi', 'bar': '666' }, func) )
    self.assertEqual( ( { 'foo': 'hi', 'fruit': 'apple' }, { 'bar': '666' } ), dict_util.partition_by_function({ 'foo': 'hi', 'bar': '666', 'fruit': 'apple' }, func) )
    
  def test_hide_passwords(self):
    self.assertEqual( {
      'username': 'fred',
      'password': '***'
    }, dict_util.hide_passwords({ 'username': 'fred', 'password': 'foo' }, [ 'password' ]) )
    
  def test_hide_passwords_with_None_values(self):
    self.assertEqual( {
      'username': 'fred',
      'password': None,
    }, dict_util.hide_passwords({ 'username': 'fred', 'password': None }, [ 'password' ]) )
    
if __name__ == '__main__':
  unittest.main()
