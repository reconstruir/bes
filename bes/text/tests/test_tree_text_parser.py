#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.text import tree_text_parser as P

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
    self.assertEqual( [], self.__parse(text) )
    
  @classmethod
  def __parse(self, text):
    options = 0
    return P.parse(text, options = options)

if __name__ == "__main__":
  unittest.main()
