#!/usr/bin/env python
#-*- coding:utf-8 -*-

import struct

class bitwise_word(object):

  ENDIAN_LE = '<'
  ENDIAN_BE = '>'
  _STRUCT_FORMATS = {
    ENDIAN_LE: {
      1: '<B',
      2: '<H',
      4: '<I',
      8: '<Q',
    },
    ENDIAN_BE    : {
      1: '>B',
      2: '>H',
      4: '>I',
      8: '>Q',
    },
  }
  
  def __init__(self, word, size):
    assert size in [ 8, 16, 24, 32, 40, 48, 56, 64 ]
    self._word = word
    self._size = size

  def __str__(self):
    return bin(self._word)

  @property
  def word(self):
    return self._word
    
  @property
  def size(self):
    return self._size

  @classmethod
  def get_bit(clazz, word, i):
    return (word >> i) & 0x1
  
  @classmethod
  def get_slice(clazz, word, start, stop):
    assert stop > start
    result = 0x0
    for i in range(start, stop):
      b = clazz.get_bit(word, i)
      shift = i - start
      result |= (b << shift)
    return result
  
  @classmethod
  def make_mask(clazz, i):
    assert n >= 0
    mask = 0x0
    for i in range(0, n):
      mask |= (0x1 << i)
    return mask
    
  def __getitem__(self, i):
    if isinstance(i, slice):
      assert self.slice_in_range(i.start, i.stop)
      return self.get_slice(self._word, i.start, i.stop)
    else:
      assert self.in_range(i)
      return self.get_bit(self._word, i)

  def __setitem__(self, i, v):
    assert v in [ 0, 1 ]
    assert isinstance(i, int)
    assert i in range(0, self._size)
    return 0

  def in_range(self, i):
    'Return True if the index i is within range of the word'
    return isinstance(i, int) and i in range(0, self._size)

  def slice_in_range(self, start, end):
    'Return True if the slice start and end are within range of the word size.'
    return start >= 0 and end <= self._size
