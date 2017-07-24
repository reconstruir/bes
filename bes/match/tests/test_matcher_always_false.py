#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.match import matcher_always_false

class TestMatcher(unittest.TestCase):

  def test_always_true_matcher(self):
    self.assertFalse( matcher_always_false().match('foo') )

if __name__ == "__main__":
  unittest.main()
