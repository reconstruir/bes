#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from water.common import water_util

class test_water_util(unittest.TestCase):

  def test_water_func_one(self):
    self.assertEqual( '666', water_util.water_func_one('666') )
  
  def test_water_func_two(self):
    self.assertEqual( '666', water_util.water_func_two('666') )
  
  def test_water_util_a_one(self):
    self.assertEqual( '666', water_util.water_util_a_one('666') )

  def test_water_util_b_one(self):
    self.assertEqual( '666', water_util.water_util_b_one('666') )

if __name__ == '__main__':
  unittest.main()
