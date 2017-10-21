#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import dict_util
from bes.system import compat

class Testobject_util(unittest.TestCase):

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

if __name__ == '__main__':
  unittest.main()
