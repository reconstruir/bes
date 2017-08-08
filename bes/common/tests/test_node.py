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
    self.assertEqual( None, n.caca_find_child('notthere') )
#    self.assertEqual( False, n.has_child('notthere') )

  def test_add_child(self):
    n = node('root')
    n.add_child('fruits')
    self.assertEqual( 1, n.num_children() )
    self.assertEqual( node('fruits'), n.caca_find_child('fruits') )
#    self.assertTrue( n.has_child('fruits') )

  def test_to_string(self):
    n = node('root')
    n.add_child('fruits')
    fruits = n.caca_find_child('fruits')
    fruits.add_child('kiwi')
    fruits.add_child('strawberry')
    fruits.add_child('melons')
    melons = fruits.caca_find_child('melons')
    melons.add_child('watermelon')
    melons.add_child('canteloupe')
    n.add_child('cheeses')
    cheeses = n.caca_find_child('cheeses')
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
    n = self._make_tree([
      'fruits/kiwi',
      'fruits/strawberry',
      'fruits/melons/watermelon',
      'fruits/melons/canteloupe',
      'cheeses/gouda',
      'cheeses/brie',
    ])

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
    
  def _ensure_paths(self, n, paths):
    for p in paths:
      n.ensure_path(p.split('/'))

  def _make_tree(self, paths):
    n = node('root')
    self._ensure_paths(n, [
      'fruits/kiwi',
      'fruits/strawberry',
      'fruits/melons/watermelon',
      'fruits/melons/canteloupe',
      'cheeses/gouda',
      'cheeses/brie',
    ])
    return n
      
  def test_find_children(self):
    n = self._make_tree([
      'fruits/kiwi',
      'fruits/strawberry',
      'fruits/melons/watermelon',
      'fruits/melons/canteloupe',
      'cheeses/gouda',
      'cheeses/brie',
    ])
    func = lambda node: node.data.startswith('gouda') or node.data.startswith('brie')
    found = n.find_children(func)
    self.assertEqual( 2, len(found) )
    self.assertEqual( 'gouda', found[0].child.data )
    self.assertEqual( 1, found[0].depth )
    self.assertEqual( 'brie', found[1].child.data )
    self.assertEqual( 1, found[1].depth )
      
if __name__ == "__main__":
  unittest.main()
