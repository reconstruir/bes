#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.key_value.key_value import key_value as KV
from bes.system.compat import compat

class test_key_value(unittest.TestCase):

  def test_str(self):
    self.assertEqual( 'foo=666', str(KV('foo', 666)) )

  def test_is_instance(self):
    self.assertEqual( True, KV('foo', 666).is_instance(compat.STRING_TYPES, compat.INTEGER_TYPES) )

if __name__ == "__main__":
  unittest.main()
