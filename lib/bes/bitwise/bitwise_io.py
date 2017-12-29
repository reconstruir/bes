#!/usr/bin/env python
#-*- coding:utf-8 -*-

import codecs

from .bitwise_unpack import bitwise_unpack
from bes.common import check

class bitwise_io(object):

  def __init__(self, stream, endian = bitwise_unpack.LE):
    self._endian = endian
    self._stream = stream

  def read_to_end(self):
    return self._stream.read()
    
  def read_bytes(self, num_bytes):
    return self._stream.read(num_bytes)
    
  def read(self, size):
    assert size in [ 1, 2, 4, 8]
    return bitwise_unpack.unpack(self._stream.read(size), size, endian = self._endian)
    
  def read_bits(self, size, slices):
    assert size in [ 1, 2, 4, 8]
    return bitwise_unpack.unpack_bits(self._stream.read(size), size, slices, endian = self._endian)
    
  def read_u8(self):
    return self.read(1)
  
  def read_u16(self):
    return self.read(2)

  def read_u32(self):
    return self.read(4)

  def read_u64(self):
    return self.read(8)

  def read_u8_bits(self, slices):
    return self.read_bits(1, slices)
    
  def read_u16_bits(self, slices):
    return self.read_bits(2, slices)
  
  def read_u32_bits(self, slices):
    return self.read_bits(4, slices)

  def read_u64_bits(self, slices):
    return self.read_bits(8, slices)

  def write_bytes(self, data, num_bytes):
    check.check_int(num_bytes, 'num_bytes')
    if len(data) < num_bytes:
      raise ValueError('data should be at least %d bytes long instead of %d' % (num_bytes, len(data)))
    self._stream.write(data[0:num_bytes])
  
  def write(self, i, size):
    assert size in [ 1, 2, 4, 8]
    self._stream.write(bitwise_unpack.pack(i, size, endian = self._endian))
    
  def write_bits(self, slices, values, size):
    self._stream.write(bitwise_unpack.pack_bits(size, slices, values, endian = self._endian))

  def write_u8(self, i):
    self.write(i, 1)

  def write_u16(self, i):
    self.write(i, 2)

  def write_u32(self, i):
    self.write(i, 4)

  def write_u64(self, i):
    self.write(i, 8)

  def write_u8_bits(self, slices, values):
    self.write_bits(slices, values, 1)

  def write_u16_bits(self, slices, values):
    self.write_bits(slices, values, 2)

  def write_u32_bits(self, slices, values):
    self.write_bits(slices, values, 4)

  def write_u64_bits(self, slices, values):
    self.write_bits(slices, values, 8)

  def write_variable_length_string(self, s, codec = 'utf-8'):
    bytes_s = s.encode(codec)
    self.write_u8(len(bytes_s))
    self.write_bytes(bytes_s, len(bytes_s))

  def read_variable_length_string(self, codec = 'utf-8'):
    s_len = self.read_u8()
    s_bytes = self.read_bytes(s_len)
    return s_bytes.decode(codec)
  
  def read_fixed_length_string(self, length, codec = 'utf-8'):
    data = self.read_bytes(length)
    data = data.replace(b'\x00', b'')
    return data.decode(codec)
    
  def write_fixed_length_string(self, s, length, codec = 'utf-8'):
    data = s.encode(codec)
    if len(data) > length:
      raise ValueError('Encoded data is too long - %d instead of %d bytes: %s' % (len(data), length, s))
    data = data.ljust(length, b'\x00')
    assert len(data) == length
    self.write_bytes(data, length)
