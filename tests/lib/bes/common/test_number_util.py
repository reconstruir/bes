#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import unittest
from bes.common.number_util import number_util
from bes.system.compat import compat

class Testnumber_util(unittest.TestCase):

  def test_int_to_base2(self):
    self.assertEqual( '1', number_util.int_to_base2(1) )
    self.assertEqual( '10', number_util.int_to_base2(2) )
    self.assertEqual( '11', number_util.int_to_base2(3) )

    self.assertEqual( '0001', number_util.int_to_base2(1, 4) )
    self.assertEqual( '0010', number_util.int_to_base2(2, 4) )
    self.assertEqual( '0011', number_util.int_to_base2(3, 4) )

    self.assertEqual( '001', number_util.int_to_base2(1, 3) )
    self.assertEqual( '010', number_util.int_to_base2(2, 3) )
    self.assertEqual( '011', number_util.int_to_base2(3, 3) )

    self.assertEqual( '01', number_util.int_to_base2(1, 2) )
    self.assertEqual( '10', number_util.int_to_base2(2, 2) )
    self.assertEqual( '11', number_util.int_to_base2(3, 2) )

    self.assertEqual( '1', number_util.int_to_base2(1, 1) )
    self.assertEqual( '10', number_util.int_to_base2(2, 1) )
    self.assertEqual( '11', number_util.int_to_base2(3, 1) )

    self.assertEqual( '1', number_util.int_to_base2(1, 0) )
    self.assertEqual( '10', number_util.int_to_base2(2, 0) )
    self.assertEqual( '11', number_util.int_to_base2(3, 0) )

  def test_is_int(self):
    self.assertEqual( True, number_util.is_int(5) )
    self.assertEqual( False, number_util.is_int(5.5) )
    self.assertEqual( True, number_util.is_int(-5) )
    self.assertEqual( False, number_util.is_int('5') )
    self.assertEqual( False, number_util.is_int('5.5') )
    self.assertEqual( False, number_util.is_int('-5') )
    self.assertEqual( False, number_util.is_int(u'5') )
    self.assertEqual( False, number_util.is_int(u'5.5') )
    self.assertEqual( False, number_util.is_int(u'-5') )
    if compat.IS_PYTHON2:
      self.assertEqual( True, number_util.is_int(long(5)) )
      self.assertEqual( True, number_util.is_int(long(-5)) )

  def test_string_is_int(self):
    self.assertEqual( True, number_util.string_is_int(5) )
    self.assertEqual( False, number_util.string_is_int(5.5) )
    self.assertEqual( True, number_util.string_is_int(-5) )
    self.assertEqual( True, number_util.string_is_int('5') )
    self.assertEqual( False, number_util.string_is_int('5.5') )
    self.assertEqual( True, number_util.string_is_int('-5') )
    self.assertEqual( True, number_util.string_is_int(u'5') )
    self.assertEqual( False, number_util.string_is_int(u'5.5') )
    self.assertEqual( True, number_util.string_is_int(u'-5') )
      
  def test_to_int(self):
    self.assertEqual( 5, number_util.to_int(5) )
    self.assertEqual( None, number_util.to_int(5.5) )
    self.assertEqual( -5, number_util.to_int(-5) )
    self.assertEqual( 5, number_util.to_int('5') )
    self.assertEqual( None, number_util.to_int('5.5') )
    self.assertEqual( -5, number_util.to_int('-5') )
    self.assertEqual( 5, number_util.to_int(u'5') )
    self.assertEqual( None, number_util.to_int(u'5.5') )
    self.assertEqual( -5, number_util.to_int(u'-5') )
    if compat.IS_PYTHON2:
      self.assertEqual( 5, number_util.to_int(long(5)) )
      self.assertEqual( -5, number_util.to_int(long(-5)) )

if __name__ == "__main__":
  unittest.main()
