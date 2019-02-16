#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import algorithm
from bes.compat import cmp

class test_algorithm(unittest.TestCase):

  def test_remove_empties(self):
    self.assertEqual( [ 'x' ], algorithm.remove_empties([ 'x', ]) )
    self.assertEqual( [ 'x' ], algorithm.remove_empties([ 'x', None ]) )
    self.assertEqual( [ 'x' ], algorithm.remove_empties([ 'x', [] ]) )
    self.assertEqual( [ 'x' ], algorithm.remove_empties([ 'x', () ]) )
    self.assertEqual( [ 'x', 0 ], algorithm.remove_empties([ 'x', 0 ]) )
    self.assertEqual( [ 'x', 0.0 ], algorithm.remove_empties([ 'x', 0.0 ]) )
    self.assertEqual( [ 'x', False ], algorithm.remove_empties([ 'x', False ]) )

  def test_unique(self):
    self.assertEqual( [ 'a', 'b', 'c' ], algorithm.unique([ 'a', 'b', 'c' ]) )
    self.assertEqual( [ 'a', 'b', 'c' ], algorithm.unique([ 'a', 'b', 'c', 'c' ]) )
    self.assertEqual( [ 'c', 'a', 'b' ], algorithm.unique([ 'c', 'a', 'b', 'c' ]) )

  def test_not_unique(self):
    self.assertEqual( [], algorithm.not_unique([ 'a', 'b', 'c' ]) )
    self.assertEqual( [ 'c' ], algorithm.not_unique([ 'a', 'b', 'c', 'c' ]) )
    self.assertEqual( [ 'c' ], algorithm.not_unique([ 'c', 'a', 'b', 'c' ]) )

  def test_binary_search(self):
    a = [ 1, 5, 7, 9, 20, 1000, 1001, 1002, 3000 ]
    comp = lambda a, b: cmp(a, b)
    self.assertEqual( 0, algorithm.binary_search(a, 1, comp) )
    self.assertEqual( -1, algorithm.binary_search(a, 0, comp) )
    self.assertEqual( -1, algorithm.binary_search(a, 2, comp) )
    self.assertEqual( 4, algorithm.binary_search(a, 20, comp) )
    self.assertEqual( 8, algorithm.binary_search(a, 3000, comp) )
    self.assertEqual( -1, algorithm.binary_search(a, 3001, comp) )

if __name__ == "__main__":
  unittest.main()
