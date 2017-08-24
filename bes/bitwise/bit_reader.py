#!/usr/bin/env python
#-*- coding:utf-8 -*-

import struct

class bit_reader(object):

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
  
  def __init__(self, stream, endian):
    self._endian = endian
    self._stream = stream
    self._current_byte = None
    self._current_byte_read_count = None
    
  def read(self, num_bits):
    assert num_bits >= 1
    assert num_bits <= 64
    num_bytes = self.num_bytes_for_bits(num_bits)
    num_odd_bits = num_bits % 8
    if num_odd_bits == 0:
      return self._read_even_bits(num_bits)
    else:
      return self._read_odd_bits(num_bits)

  def _read_even_bits(self, num_bits):
    assert (num_bits % 8) == 0
    num_bytes = self.num_bytes_for_bits(num_bits)
    data = self._read_bytes(num_bytes)
    assert num_bytes in [ 1, 2, 4, 8 ]
    result = struct.unpack(self._STRUCT_FORMATS[self._endian][num_bytes], data)[0]
    return result
  
  def _read_odd_bits(self, num_bits):
    assert (num_bits % 8) != 0
    assert num_bits in range(1, 7)

    if not self._current_byte:
      self._current_byte = self.read_int8()
      self._current_byte_read_count = 0

    assert self._current_byte_read_count in range(0, 8)
      
    num_to_shift = num_bits + self._current_byte_read_count
    shifted = self._current_byte >> (8 - (num_to_shift))
    result = shifted & self._make_mask(num_bits)
    self._current_byte_read_count += num_bits
    assert self._current_byte_read_count <= 8
    return result

  @classmethod
  def _make_mask(clazz, n):
    assert n >= 0
    mask = 0x0
    for i in range(0, n):
      mask |= (0x1 << i)
    return mask
  
  @classmethod
  def num_bytes_for_bits(clazz, num_bits):
    num_odd_bits = num_bits % 8
    num_bytes = num_bits / 8
    if num_odd_bits > 0:
      num_bytes += 1
    return num_bytes

#  size = struct.unpack('<H', fin.read(2))[0]
  
  def _read_bytes(self, num_bytes):
    return self._stream.read(num_bytes)

  def read_word(self, size):
    assert size in [ 1, 2, 4, 8 ]
    return struct.unpack(self._STRUCT_FORMATS[self._endian][size], self._read_bytes(size))[0]

  def read_int8(self):
    return self.read_word(1)
  
  def read_int16(self):
    return self.read_word(2)
  
  def read_int32(self):
    return self.read_word(4)
  
  def read_int64(self):
    return self.read_word(8)

  def decode_bits(self, word, size, offset, num):
    assert size in [ 1, 2, 4, 8 ]
    size_in_bits = size * 8
    shifted = word >> (size_in_bits - num)
    mask = self._make_mask(num)
    return shifter & mask

  size = 3
  size_in_bits = 12
  
  12 - 12
  
  
    
    #  origin = (caca >> 14) & 3
#  tagged = (caca >> 13) & 1
#  addressable = (caca >> 12) & 1
#  protocol = caca & 4095

  
