#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test, hexdata

class test_hex_data(unit_test):

  def xtest_string_to_bytes(self):
    self.assertEqual( b'\x86\xff\x00T', hexdata.string_to_bytes('86 ff 00 54') )
    
  def test_bytes_to_string(self):
    self.assertEqual( '86 ff 00 54', hexdata.bytes_to_string(b'\x86\xff\x00T') )
    
if __name__ == '__main__':
  unit_test.main()
