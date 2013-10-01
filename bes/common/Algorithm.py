#!/usr/bin/env python
#-*- coding:utf-8 -*-

import inspect, new, unittest

class Algorithm(object):
  'Algorithm'

  @staticmethod
  def remove_empties(l, recurse = True):
    'Return a list of the non empty items in l'
    assert isinstance(l, list)
    def is_empty(x):
      return x in [ (), [], None, '' ]
    result = [ x for x in l if not is_empty(x) ]
    for i in range(0, len(result)):
      if isinstance(result[i], list):
        result[i] = Algorithm.remove_empties(result[i])
    return result

class TestAlgorithm(unittest.TestCase):

  def test_remove_empties(self):
    self.assertEqual( [ 'x' ], Algorithm.remove_empties([ 'x', ]) )
    self.assertEqual( [ 'x' ], Algorithm.remove_empties([ 'x', None ]) )
    self.assertEqual( [ 'x' ], Algorithm.remove_empties([ 'x', [] ]) )
    self.assertEqual( [ 'x' ], Algorithm.remove_empties([ 'x', () ]) )
    self.assertEqual( [ 'x', 0 ], Algorithm.remove_empties([ 'x', 0 ]) )
    self.assertEqual( [ 'x', 0.0 ], Algorithm.remove_empties([ 'x', 0.0 ]) )
    self.assertEqual( [ 'x', False ], Algorithm.remove_empties([ 'x', False ]) )

if __name__ == "__main__":
  unittest.main()
