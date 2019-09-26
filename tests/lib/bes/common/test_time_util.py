#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest

from datetime import datetime as DT

from bes.common.time_util import time_util

class test_time_util(unittest.TestCase):

  def test_timestamp_parse(self):
    f = time_util.timestamp_parse
    self.assertEqual( DT(1999, 1, 1, 1, 1, 1), f('1999-01-01-01-01-01') )
    self.assertEqual( DT(1999, 1, 1, 1, 1, 1), f('1999:01:01:01:01:01', delimiter = ':' ) )
    self.assertEqual( DT(1999, 1, 1, 1, 1, 1, .66), f('1999-01-01-01-01-01-660000', milliseconds = True) )
  
  def xtest_format_for_timestamp(self):
    f = time_util.format_for_timestamp
    self.assertEqual( '1999-01-01-01-01-01', f(datetime(year = 1999, month = 1, day = 1, hour = 1, minute = 1, second = 1)) )

if __name__ == "__main__":
  unittest.main()
