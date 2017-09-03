#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.test import unit_test_helper
from bes.common import math_util

class test_math_util(unit_test_helper):

  def test_clamp(self):
    self.assertEqual( 0.0, math_util.clamp(-1.0, 0.0, 100.0) )
    self.assertEqual( 100.0, math_util.clamp(100.1, 0.0, 100.0) )

if __name__ == "__main__":
  unit_test_helper.main()
