#!/usr/bin/env python
#-*- coding:utf-8 -*-

import struct
from .bitwise_word import bitwise_word

class bitwise_unpack(object):

  LE = '<'
  BE = '>'
  
  _UNPACK_FORMATS = {
    LE: {
      1: '<B',
      2: '<H',
      4: '<I',
      8: '<Q',
    },
    BE: {
      1: '>B',
      2: '>H',
      4: '>I',
      8: '>Q',
    },
  }

  _PACK_FORMATS = {
    LE: {
      1: '< B',
      2: '< H',
      4: '< I',
      8: '< Q',
    },
    BE: {
      1: '> B',
      2: '> H',
      4: '> I',
      8: '> Q',
    },
  }

  DEFAULT_ENDIAN = LE
  
  @classmethod
  def unpack(clazz, data, size, endian = DEFAULT_ENDIAN):
    assert size in [ 1, 2, 4, 8 ]
    return struct.unpack(clazz._UNPACK_FORMATS[endian][size], data)[0]

  @classmethod
  def unpack_bits(clazz, data, size, slices, endian = DEFAULT_ENDIAN):
    assert size in [ 1, 2, 4, 8 ]
    num_bits = size * 8
    validated_slices = clazz.validate_slices(slices, num_bits)
    if not validated_slices:
      raise RuntimeError('Invalid slice sequence: %s' % (str(slices)))
    word = bitwise_word(clazz.unpack(data, size, endian = endian), num_bits)
    result = []
    for s in validated_slices:
      result.append(word[s])
    return tuple(result)

  @classmethod
  def unpack_u8(clazz, data, endian = DEFAULT_ENDIAN):
    return clazz.unpack(data, 1, endian = endian)
  
  @classmethod
  def unpack_u16(clazz, data, endian = DEFAULT_ENDIAN):
    return clazz.unpack(data, 2, endian = endian)
  
  @classmethod
  def unpack_u32(clazz, data, endian = DEFAULT_ENDIAN):
    return clazz.unpack(data, 4, endian = endian)
  
  @classmethod
  def unpack_u64(clazz, data, endian = DEFAULT_ENDIAN):
    return clazz.unpack(data, 64, endian = endian)
  
  @classmethod
  def unpack_u8_bits(clazz, data, slices, endian = DEFAULT_ENDIAN):
    return clazz.unpack_bits(data, 1, slices, endian = endian)

  @classmethod
  def unpack_u16_bits(clazz, data, slices, endian = DEFAULT_ENDIAN):
    return clazz.unpack_bits(data, 2, slices, endian = endian)

  @classmethod
  def unpack_u32_bits(clazz, data, slices, endian = DEFAULT_ENDIAN):
    return clazz.unpack_bits(data, 4, slices, endian = endian)

  @classmethod
  def unpack_u64_bits(clazz, data, slices, endian = DEFAULT_ENDIAN):
    return clazz.unpack_bits(data, 8, slices, endian = endian)

  @classmethod
  def pack(clazz, i, size, endian = DEFAULT_ENDIAN):
    assert size in [ 1, 2, 4, 8 ]
    format = clazz._PACK_FORMATS[endian][size]
    result = struct.Struct(format).pack(i)
    return result

  @classmethod
  def pack_bits(clazz, size, slices, values, endian = DEFAULT_ENDIAN):
    assert size in [ 1, 2, 4, 8 ]
    num_bits = size * 8
    validated_slices = clazz.validate_slices(slices, num_bits)
    if not validated_slices:
      raise RuntimeError('Invalid slice sequence: %s' % (str(slices)))
    if not isinstance(values, ( list, tuple )):
      raise RuntimeError('values should be a list or tuple: ' % (str(values)))
    if len(values) != len(slices):
      raise RuntimeError('values and slices should be the same length')
    word = bitwise_word(0x0, num_bits)
    for s, value in zip(validated_slices, values):
      word[s] = value
    return clazz.pack(word.word, size, endian = endian)
    
  @classmethod
  def pack_u8(clazz, i, endian = DEFAULT_ENDIAN):
    return clazz.pack(i, 1, endian = endian)
  
  @classmethod
  def pack_u16(clazz, i, endian = DEFAULT_ENDIAN):
    return clazz.pack(i, 2, endian = endian)
  
  @classmethod
  def pack_u32(clazz, i, endian = DEFAULT_ENDIAN):
    return clazz.pack(i, 4, endian = endian)
  
  @classmethod
  def pack_u64(clazz, i, endian = DEFAULT_ENDIAN):
    return clazz.pack(i, 8, endian = endian)

  @classmethod
  def pack_u8_bits(clazz, slices, values, endian = DEFAULT_ENDIAN):
    return self.pack_bits(1, slices, values, endian = endian)
    
  @classmethod
  def pack_u16_bits(clazz, slices, values, endian = DEFAULT_ENDIAN):
    return self.pack_bits(2, slices, values, endian = endian)
    
  @classmethod
  def pack_u32_bits(clazz, slices, values, endian = DEFAULT_ENDIAN):
    return self.pack_bits(4, slices, values, endian = endian)
    
  @classmethod
  def pack_u64_bits(clazz, slices, values, endian = DEFAULT_ENDIAN):
    return self.pack_bits(8, slices, values, endian = endian)
    
  # FIXME: move validation methods to bitwise_word
  @classmethod
  def validate_slice(clazz, s, size):
    if isinstance(s, ( list, tuple )):
      if len(s) != 2:
        return None
      s = slice(s[0], s[1])
    if not isinstance(s, slice):
      return None
    if s.start >= 0 and s.stop <= size and s.step in [ None, 1 ]:
      return s
    return None
  
  @classmethod
  def validate_slices(clazz, l, size):
    if not isinstance(l, ( tuple, list )):
      return None
    result = [ clazz.validate_slice(i, size) for i in l ]
    if None in result:
      return None
    return result
  
