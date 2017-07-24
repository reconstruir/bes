#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.match import matcher_always_true

class TestMatcher(unittest.TestCase):

  def test_always_true_matcher(self):
    self.assertTrue( matcher_always_true().match('foo') )

if __name__ == "__main__":
  unittest.main()
