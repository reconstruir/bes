#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.variable.variable_parser import variable_parser as P, variable_token as V
from bes.common import point

class test_variable_parser(unittest.TestCase):
    
  def test_simple_bracket(self):
    self.assertEqual( [ V('foo', 'foo', None, point(1, 1), point(6, 1)) ], self._parse('${foo}') )
    self.assertEqual( [ V('foo', 'foo', None, point(1, 1), point(6, 1)) ], self._parse('${foo}x') )
    self.assertEqual( [ V('foo', 'foo', None, point(2, 1), point(7, 1)) ], self._parse('x${foo}') )
    self.assertEqual( [ V('foo', 'foo', None, point(2, 1), point(7, 1)) ], self._parse('x${foo}x') )
    self.assertEqual( [ V('foo', 'foo', None, point(1, 1), point(6, 1)) ], self._parse('${foo} ') )
    self.assertEqual( [ V('foo', 'foo', None, point(2, 1), point(7, 1)) ], self._parse(' ${foo}') )
    self.assertEqual( [ V('foo', 'foo', None, point(2, 1), point(7, 1)) ], self._parse(' ${foo} ') )
    
  def test_simple_parentesis(self):
    self.assertEqual( [ V('foo', 'foo', None, point(1, 1), point(6, 1)) ], self._parse('$(foo)') )
    
  def test_simple(self):
    self.assertEqual( [ V('foo', 'foo', None, point(1, 1), point(4, 1)) ], self._parse('$foo') )
    self.assertEqual( [ V('foo', 'foo', None, point(1, 1), point(4, 1)) ], self._parse('$foo ') )
    self.assertEqual( [ V('foo', 'foo', None, point(2, 1), point(5, 1)) ], self._parse(' $foo') )
    self.assertEqual( [ V('foo', 'foo', None, point(2, 1), point(5, 1)) ], self._parse(' $foo ') )
    self.assertEqual( [ V('foo', 'foo', None, point(2, 1), point(5, 1)) ], self._parse('x$foo:') )
    
  @classmethod
  def _parse(self, text):
    return [ v for v in P.parse(text) ]

if __name__ == "__main__":
  unittest.main()
