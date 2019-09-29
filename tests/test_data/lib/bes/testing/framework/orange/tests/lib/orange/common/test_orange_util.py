#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from orange.common import orange_util

class test_orange_util(unittest.TestCase):

  def test_orange_func_one(self):
    self.assertEqual( 'a', orange_util.orange_func_one('a') )
  
  def test_orange_func_two(self):
    self.assertEqual( 'a', orange_util.orange_func_two('a') )
  
  def test_util_a_one(self):
    self.assertEqual( 'a', orange_util.util_a_one('a') )

  def test_util_b_one(self):
    self.assertEqual( 'a', orange_util.util_a_one('b') )

if __name__ == '__main__':
  unittest.main()
