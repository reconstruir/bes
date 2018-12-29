#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import tuple_util
from collections import namedtuple

class test_tuple_util(unittest.TestCase):

  def test_dict_to_named_tuple(self):
    d = { 'f': 5,
          'foo': 5,
          'bar': 'hi',
          'caca': object,
          'a b c': 666,
          '1foo': False,
          'foo1': False,
          'foo_': False,
          '_foo': False,
          '_': False,
    }
    t = tuple_util.dict_to_named_tuple('n', d)
    self.assertEqual( sorted([ 'caca', 'bar', 'foo', 'foo1', 'foo_', 'f' ]), sorted(list(t._fields)) )

  def test_clone(self):
    T = namedtuple('T', 'foo, bar')
    a = T(5, 'hello')
    self.assertEqual( ( 5, 'hello' ), tuple_util.clone(a) )

  def test_clone_with_mutations(self):
    T = namedtuple('T', 'foo, bar')
    a = T(5, 'hello')
    self.assertEqual( ( 5, 'bye' ), tuple_util.clone(a, mutations = { 'bar': 'bye' }) )
    self.assertEqual( ( 9, 'bye2' ), tuple_util.clone(a, mutations = { 'foo': 9, 'bar': 'bye2' }) )

  def test_clone_with_mutations_invalid_field(self):
    T = namedtuple('T', 'foo, bar')
    a = T(5, 'hello')
    with self.assertRaises(ValueError) as ctx:
      tuple_util.clone(a, mutations = { 'kiwi': 'hi' })

if __name__ == '__main__':
  unittest.main()
