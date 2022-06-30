#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from datetime import datetime

from bes.common.time_util import time_util

class test_time_util(unit_test):

  def test_ms_to_tuple(self):
    self.assertEqual( ( 0, 0, 1 ), time_util.ms_to_tuple(1000) )

if __name__ == '__main__':
  unit_test.main()
