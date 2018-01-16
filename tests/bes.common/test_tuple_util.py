#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import tuple_util

class Testobject_util(unittest.TestCase):

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

if __name__ == '__main__':
  unittest.main()
