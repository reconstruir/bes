#!/usr/bin/env python
#-*- coding:utf-8 -*-

import unittest

class number_util(object):
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

    if isinstance(x, basestring):
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
  
