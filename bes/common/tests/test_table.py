#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.common import table

class test_table(unittest.TestCase):

  def test_empty(self):
    t = table()
    self.assertEqual( 0, t.width )
    self.assertEqual( 0, t.height )

  def test_not_empty(self):
    t = table(10, 10)
    self.assertEqual( 10, t.width )
    self.assertEqual( 10, t.height )

  def test_set(self):
    t = table(10, 10)
    t.set(0, 0, 1)
    t.set(5, 5, 5)
    t.set(9, 9, 9)
    self.assertEqual( 5, t.get(5, 5) )
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 9, t.get(9, 9) )

if __name__ == "__main__":
  unittest.main()
