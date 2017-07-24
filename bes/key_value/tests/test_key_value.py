#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.key_value import key_value as KV

class test_key_value(unittest.TestCase):

  def test_str(self):
    self.assertEqual( 'foo=666', str(KV('foo', 666)) )

if __name__ == "__main__":
  unittest.main()
