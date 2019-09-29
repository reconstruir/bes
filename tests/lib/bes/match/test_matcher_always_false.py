#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.match.matcher_always_false import matcher_always_false

class TestMatcher(unittest.TestCase):

  def test_always_true_matcher(self):
    self.assertFalse( matcher_always_false().match('foo') )

if __name__ == "__main__":
  unittest.main()
