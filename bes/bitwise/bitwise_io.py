#!/usr/bin/env python
#-*- coding:utf-8 -*-

from bitwise_unpack import bitwise_unpack

class bitwise_io(object):

  def __init__(self, stream, endian = bitwise_unpack.LE):
    self._endian = endian
    self._stream = stream

  def skip(self, num_bytes):
    self._stream.read(num_bytes)
    
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

