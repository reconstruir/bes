#!/usr/bin/env python
#-*- coding:utf-8 -*-

import struct

# FIXME use slice

class bitwise_word(object):

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
  def set_bit(clazz, word, i, v):
    assert v in [ 0, 1 ]
    return word | (v << i)
  
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
  def to_bit_string(clazz, word, size):
    return bin(word)[2:].zfill(size)
    
  @classmethod
  def set_slice(clazz, word, start, stop, v):
    assert stop > start
    mask = clazz.make_mask(stop - start + 0)
    v = v & mask
#    print "   word: ", clazz.to_bit_string(word, 8)
#    print "      v: ", clazz.to_bit_string(v, 8)
#    print "shifted: ", clazz.to_bit_string(v << start, 8)
    result = word | (v << start)
#    print " result: ", clazz.to_bit_string(result, 8)
    return result
  
  @classmethod
  def make_mask(clazz, n):
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
      if not self.in_range(i):
        raise RuntimeError('Index out of range.  Should be (%d, %d): %d' % (0, self._size, i))
      return self.get_bit(self._word, i)

  def __setitem__(self, i, v):
    if isinstance(i, slice):
      assert self.slice_in_range(i.start, i.stop)
      self._word = self.set_slice(self._word, i.start, i.stop, v)
    else:
      assert self.in_range(i)
      self._word = self.set_bit(self._word, i, v)

  def in_range(self, i):
    'Return True if the index i is within range of the word'
    return isinstance(i, int) and i in range(0, self._size)

  # FIXME: add support for nevative slice bounds
  def slice_in_range(self, start, end):
    'Return True if the slice start and end are within range of the word size.'
    return start >= 0 and end <= self._size
