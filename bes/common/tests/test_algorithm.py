#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import algorithm

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

if __name__ == "__main__":
  unittest.main()
