#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.common.hash_util import hash_util

class test_hash_util(unit_test):
  
  def test_hash_string_sha256(self):
    self.assertEqual( '1a5afeda973d776e31d1d7266f184468f84d99bed311d88d3dcb67015934f9f9',
                      hash_util.hash_string_sha256('kiwi') )

  def test_hash_string_unsigned(self):
    self.assertEqual( 70489398846495728855084937399463962257135627889, hash_util.hash_string_unsigned('kiwi') )
    self.assertEqual( 35627889, hash_util.hash_string_unsigned('kiwi', 8) )
    self.assertEqual( 7889, hash_util.hash_string_unsigned('kiwi', 4) )
    
if __name__ == '__main__':
  unit_test.main()
