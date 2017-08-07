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

if __name__ == "__main__":
  unittest.main()
