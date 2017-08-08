#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import node

class test_node(unittest.TestCase):

  def test___init__(self):
    n = node('root')
    self.assertEqual( 0, n.num_children() )
    self.assertEqual( 'root', n.data )
    self.assertEqual( None, n.find_child('notthere') )
    self.assertEqual( False, n.has_child('notthere') )

  def test_add_child(self):
    n = node('root')
    n.add_child('fruits')
    self.assertEqual( 1, n.num_children() )
    self.assertEqual( node('fruits'), n.find_child('fruits') )
    self.assertTrue( n.has_child('fruits') )

  def test_to_string(self):
    n = node('root')
    n.add_child('fruits')
    fruits = n.find_child('fruits')
    fruits.add_child('kiwi')
    fruits.add_child('strawberry')
    fruits.add_child('melons')
    melons = fruits.find_child('melons')
    melons.add_child('watermelon')
    melons.add_child('canteloupe')
    n.add_child('cheeses')
    cheeses = n.find_child('cheeses')
    cheeses.add_child('gouda')
    cheeses.add_child('brie')

    expected='''root
  fruits
    kiwi
    strawberry
    melons
      watermelon
      canteloupe
  cheeses
    gouda
    brie
'''
    self.assertEqual( expected, str(n) )

  def test_ensure_path(self):
    n = node('root')
    n.ensure_path([ 'fruits', 'kiwi' ])
    n.ensure_path([ 'fruits', 'strawberry' ])
    n.ensure_path([ 'fruits', 'melons', 'watermelon' ])
    n.ensure_path([ 'fruits', 'melons', 'canteloupe' ])
    n.ensure_path([ 'cheeses', 'gouda' ])
    n.ensure_path([ 'cheeses', 'brie' ])

    expected='''root
  fruits
    kiwi
    strawberry
    melons
      watermelon
      canteloupe
  cheeses
    gouda
    brie
'''
    self.assertEqual( expected, str(n) )
if __name__ == "__main__":
  unittest.main()
