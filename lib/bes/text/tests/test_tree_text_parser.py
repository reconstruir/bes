#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.text import tree_text_parser as P
from bes.common import node

class test_tree_text_parser(unittest.TestCase):

  def test_simple(self):
    text = '''
fruits
  apple
  berries
    blueberries
    strawberries
  melons
    watermelon
cheeses
  parmessan
  asiago
'''
    expected = node('root')
    expected.ensure_path([ 'fruits', 'apple' ])
    expected.ensure_path([ 'fruits', 'berries', 'blueberries' ])
    expected.ensure_path([ 'fruits', 'berries', 'strawberries' ])
    expected.ensure_path([ 'fruits', 'melons', 'watermelon' ])
    expected.ensure_path([ 'cheeses', 'parmessan' ])
    expected.ensure_path([ 'cheeses', 'asiago' ])
    
    self.assertEqual( expected, P.parse(text) )
    
if __name__ == "__main__":
  unittest.main()
