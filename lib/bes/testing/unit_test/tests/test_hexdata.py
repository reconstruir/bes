#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test, hexdata

class test_hex_data(unit_test):

  def test_caca(self):
    data = '86 00 00 34'
    #self.assertEqual( '', hexdata.string_to_bytes(data) )
    
if __name__ == '__main__':
  unit_test.main()
