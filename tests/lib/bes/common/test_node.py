#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common.node import node

class test_node(unittest.TestCase):

  def test___init__(self):
    n = node('root')
    self.assertEqual( 0, n.num_children() )
    self.assertEqual( 'root', n.data )
    self.assertEqual( None, n.find_child_by_data('notthere') )
#    self.assertEqual( False, n.has_child('notthere') )

  def test_add_child(self):
    n = node('root')
    n.add_child('fruits')
    self.assertEqual( 1, n.num_children() )
    self.assertEqual( node('fruits'), n.find_child_by_data('fruits') )
#    self.assertTrue( n.has_child('fruits') )

  def test_to_string(self):
    n = node('root')
    n.add_child('fruits')
    fruits = n.find_child_by_data('fruits')
    fruits.add_child('kiwi')
    fruits.add_child('strawberry')
    fruits.add_child('melons')
    melons = fruits.find_child_by_data('melons')
    melons.add_child('watermelon')
    melons.add_child('canteloupe')
    n.add_child('cheeses')
    cheeses = n.find_child_by_data('cheeses')
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
    brie'''
    self.assertMultiLineEqual( expected, str(n) )

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
    brie'''
    self.assertMultiLineEqual( expected, str(n) )
    
  def _make_tree(self, paths):
    n = node('root')
    for p in paths:
      n.ensure_path(p.split('/'))
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

  def test_find_children_nested(self):
    n = self._make_tree([
      'fruits/kiwi',
      'fruits/strawberry',
      'fruits/melons/watermelon',
      'fruits/melons/canteloupe',
      'cheeses/gouda',
      'cheeses/brie',
      'pies/fruit_pies/kiwi',
      'pies/fruit_pies/strawberry',
    ])
    func = lambda node: node.data.startswith('kiwi') or node.data.startswith('strawberry')
    found = n.find_children(func)
    self.assertEqual( 4, len(found) )
    self.assertEqual( 'kiwi', found[0].child.data )
    self.assertEqual( 1, found[0].depth )
    self.assertEqual( 'strawberry', found[1].child.data )
    self.assertEqual( 1, found[1].depth )
    self.assertEqual( 'kiwi', found[2].child.data )
    self.assertEqual( 2, found[2].depth )
    self.assertEqual( 'strawberry', found[3].child.data )
    self.assertEqual( 2, found[3].depth )

  def test_find_child(self):
    n = self._make_tree([
      'fruits/kiwi',
      'fruits/strawberry',
      'fruits/melons/watermelon',
      'fruits/melons/canteloupe',
      'cheeses/gouda',
      'cheeses/brie',
    ])
    func = lambda node: node.data.startswith('gouda') or node.data.startswith('brie')
    found = n.find_child(func)
    self.assertEqual( 'gouda', found.data )

  def test_flat_paths(self):
    r = node('root')
    r.ensure_path([ 'cheese', 'blue' ])
    r.ensure_path([ 'cheese', 'brie' ])
    r.ensure_path([ 'cheese', 'gouda' ])
    r.ensure_path([ 'foo' ])
    r.ensure_path([ 'fruit', 'apple' ])
    r.ensure_path([ 'fruit', 'kiwi' ])
    r.ensure_path([ 'fruit', 'melon', 'canteloupe' ])
    r.ensure_path([ 'fruit', 'melon', 'watermelon' ])
    r.ensure_path([ 'wine', 'chianti' ])
    r.ensure_path([ 'wine', 'sancere' ])
    paths = sorted(r.flat_paths())
    self.assertEqual( [
      [ 'root', 'cheese', 'blue' ],
      [ 'root', 'cheese', 'brie' ],
      [ 'root', 'cheese', 'gouda' ],
      [ 'root', 'foo' ],
      [ 'root', 'fruit', 'apple' ],
      [ 'root', 'fruit', 'kiwi' ],
      [ 'root', 'fruit', 'melon', 'canteloupe' ],
      [ 'root', 'fruit', 'melon', 'watermelon' ],
      [ 'root', 'wine', 'chianti' ],
      [ 'root', 'wine', 'sancere' ],
    ], [ x.path for x in paths ] )

  def test_find_child(self):
    n = self._make_tree([
      'fruits/kiwi',
      'fruits/strawberry',
      'fruits/melons/watermelon',
      'fruits/melons/canteloupe',
      'cheeses/gouda',
      'cheeses/brie',
    ])
    self.assertEqual( 'kiwi', n.find_child_by_path_data([ 'fruits', 'kiwi' ]).data )

if __name__ == "__main__":
  unittest.main()
