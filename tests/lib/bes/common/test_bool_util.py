#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
from bes.common.bool_util import bool_util

class test_bool_util(unit_test):

  def test_parse_bool(self):
    self.assertEqual( True, bool_util.parse_bool(True) )
    self.assertEqual( True, bool_util.parse_bool('True') )
    self.assertEqual( True, bool_util.parse_bool('true') )
    self.assertEqual( True, bool_util.parse_bool('t') )
    self.assertEqual( True, bool_util.parse_bool('1') )
    self.assertEqual( True, bool_util.parse_bool(1) )
    self.assertEqual( True, bool_util.parse_bool(2) )

    self.assertEqual( False, bool_util.parse_bool(False) )
    self.assertEqual( False, bool_util.parse_bool('False') )
    self.assertEqual( False, bool_util.parse_bool('false') )
    self.assertEqual( False, bool_util.parse_bool('f') )
    self.assertEqual( False, bool_util.parse_bool('0') )
    self.assertEqual( False, bool_util.parse_bool(0) )
    
if __name__ == "__main__":
  unit_test.main()
