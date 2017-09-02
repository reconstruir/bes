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

  def test_get_empty(self):
    t = table(10, 10)
    self.assertEqual( None, t.get(0, 0) )

  def test_set_get(self):
    t = table(2, 2)
    t.set(0, 0, 1)
    t.set(0, 1, 2)
    t.set(1, 0, 3)
    t.set(1, 1, 4)
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 3, t.get(1, 0) )
    self.assertEqual( 4, t.get(1, 1) )

  def test_resize_shrink(self):
    t = table(3, 3)
    t.set(0, 0, 1)
    t.set(0, 1, 2)
    t.set(0, 2, 3)
    t.set(1, 0, 4)
    t.set(1, 1, 5)
    t.set(1, 2, 6)
    self.assertEqual( 3, t.width )
    self.assertEqual( 3, t.height )
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 3, t.get(0, 2) )
    self.assertEqual( 4, t.get(1, 0) )
    self.assertEqual( 5, t.get(1, 1) )
    self.assertEqual( 6, t.get(1, 2) )
    t.resize(2, 2)
    self.assertEqual( 2, t.width )
    self.assertEqual( 2, t.height )
    self.assertEqual( 1, t.get(0, 0) )
    self.assertEqual( 2, t.get(0, 1) )
    self.assertEqual( 4, t.get(1, 0) )
    self.assertEqual( 5, t.get(1, 1) )

if __name__ == "__main__":
  unittest.main()
