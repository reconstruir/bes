#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common.size import size

class test_size(unittest.TestCase):

  def test_str(self):
    self.assertEqual( '4x5', str(size(4, 5)) )
    self.assertEqual( '0x0', str(size(0, 5)) )
    self.assertEqual( '0x0', str(size(5, 0)) )

  def test_eq(self):
    self.assertEqual( size(5, 5), size(5, 5) )
    self.assertNotEqual( size(5, 5), size(5, 4) )

  def test___init__(self):
    self.assertEqual( size(0, 0), size(5) )
    self.assertEqual( size(0, 0), size() )

if __name__ == "__main__":
  unittest.main()
