#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.testing.unit_test import unit_test
from bes.properties_file_v2.properties_file_formatter_plain import properties_file_formatter_plain as F

class test_properties_formatter_plain(unit_test):

  def test_delimiter(self):
    self.assertEqual( '=', F().delimiter() )
    
if __name__ == '__main__':
  unit_test.main()
