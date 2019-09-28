#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest

from datetime import datetime as DT
#from datetime import timezone as TZ

from bes.common.timestamp import timestamp as T

class test_timestamp(unittest.TestCase):

  def test_parse(self):
    self.assertEqual( DT(1999, 1, 1, 1, 1, 1, 12), T.parse('1999-01-01-01-01-01-000012') )
    self.assertEqual( DT(1999, 1, 1, 1, 1, 1), T.parse('1999-01-01-01-01-01') )
    self.assertEqual( DT(1999, 1, 1, 1, 1), T.parse('1999-01-01-01-01') )
    self.assertEqual( DT(1999, 1, 1, 1), T.parse('1999-01-01-01') )
    self.assertEqual( DT(1999, 1, 1), T.parse('1999-01-01') )

  def test_parse_invalid(self):
    with self.assertRaises(ValueError) as ctx:
      T.parse('1999-13-01-01-01-01') 
    
    with self.assertRaises(ValueError) as ctx:
      T.parse('1999-13-01-01-01-01')
      
  def test_to_string(self):
    self.assertEqual( '1999-01-01-01-01-01', T.to_string(DT(1999, 1, 1, 1, 1, 1)) )
    self.assertEqual( '1999-01-01-01-01-01-000000-UTC', T.to_string(DT(1999, 1, 1, 1, 1, 1), timezone = 'UTC') )
    self.assertEqual( '1999-01-01-01-01-01-000000', T.to_string(DT(1999, 1, 1, 1, 1, 1), microsecond = True) )

if __name__ == "__main__":
  unittest.main()
