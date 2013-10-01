#!/usr/bin/env python
#-*- coding:utf-8 -*-

import unittest

class NumberUtil(object):
  'Number util'

  @classmethod
  def hex_to_bits(clazz, hex, min_num_digits = 0):
    'Return Parse a hex string into an integer'
    value_base10 = int(hex, 16)
    return clazz.int_to_base2(value_base10, min_num_digits)

  @classmethod
  def int_to_base2(clazz, n, min_num_digits = 0):
    result = ''
    if n < 0:
      raise ValueError, 'n must be positive'
    if n == 0:
      return '0'.zfill(min_num_digits)
    while n > 0:
      result = str(n % 2) + result
      n = n >> 1
    return result.zfill(min_num_digits)

  @classmethod
  def is_int(clazz, x):
    'Return True if x is an int.'
    if isinstance(x, (int, long)):
      return True

    if isinstance(x, (str, unicode)):
      try:
        int(x)
        return True
      except:
        pass
    return False

  @classmethod
  def to_int(clazz, x):
    'Return x as an int or None if x is not an int.'
    if not clazz.is_int(x):
      return None
    return int(x)
  
class TestNumberUtil(unittest.TestCase):

  def test_int_to_base2(self):
    self.assertEqual( '1', NumberUtil.int_to_base2(1) )
    self.assertEqual( '10', NumberUtil.int_to_base2(2) )
    self.assertEqual( '11', NumberUtil.int_to_base2(3) )

    self.assertEqual( '0001', NumberUtil.int_to_base2(1, 4) )
    self.assertEqual( '0010', NumberUtil.int_to_base2(2, 4) )
    self.assertEqual( '0011', NumberUtil.int_to_base2(3, 4) )

    self.assertEqual( '001', NumberUtil.int_to_base2(1, 3) )
    self.assertEqual( '010', NumberUtil.int_to_base2(2, 3) )
    self.assertEqual( '011', NumberUtil.int_to_base2(3, 3) )

    self.assertEqual( '01', NumberUtil.int_to_base2(1, 2) )
    self.assertEqual( '10', NumberUtil.int_to_base2(2, 2) )
    self.assertEqual( '11', NumberUtil.int_to_base2(3, 2) )

    self.assertEqual( '1', NumberUtil.int_to_base2(1, 1) )
    self.assertEqual( '10', NumberUtil.int_to_base2(2, 1) )
    self.assertEqual( '11', NumberUtil.int_to_base2(3, 1) )

    self.assertEqual( '1', NumberUtil.int_to_base2(1, 0) )
    self.assertEqual( '10', NumberUtil.int_to_base2(2, 0) )
    self.assertEqual( '11', NumberUtil.int_to_base2(3, 0) )

  def test_is_int(self):
    self.assertEqual( True, NumberUtil.is_int(5) )
    self.assertEqual( False, NumberUtil.is_int(5.5) )
    self.assertEqual( True, NumberUtil.is_int(-5) )
    self.assertEqual( True, NumberUtil.is_int('5') )
    self.assertEqual( False, NumberUtil.is_int('5.5') )
    self.assertEqual( True, NumberUtil.is_int('-5') )
    self.assertEqual( True, NumberUtil.is_int(u'5') )
    self.assertEqual( False, NumberUtil.is_int(u'5.5') )
    self.assertEqual( True, NumberUtil.is_int(u'-5') )
    self.assertEqual( True, NumberUtil.is_int(long(5)) )
    self.assertEqual( True, NumberUtil.is_int(long(-5)) )

  def test_to_int(self):
    self.assertEqual( 5, NumberUtil.to_int(5) )
    self.assertEqual( None, NumberUtil.to_int(5.5) )
    self.assertEqual( -5, NumberUtil.to_int(-5) )
    self.assertEqual( 5, NumberUtil.to_int('5') )
    self.assertEqual( None, NumberUtil.to_int('5.5') )
    self.assertEqual( -5, NumberUtil.to_int('-5') )
    self.assertEqual( 5, NumberUtil.to_int(u'5') )
    self.assertEqual( None, NumberUtil.to_int(u'5.5') )
    self.assertEqual( -5, NumberUtil.to_int(u'-5') )
    self.assertEqual( 5, NumberUtil.to_int(long(5)) )
    self.assertEqual( -5, NumberUtil.to_int(long(-5)) )

if __name__ == "__main__":
  unittest.main()
