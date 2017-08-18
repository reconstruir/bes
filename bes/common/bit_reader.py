#!/usr/bin/env python
#-*- coding:utf-8 -*-

class bit_reader(object):

  ENDIAN_LITTLE = '<'
  ENDIAN_BIG = '>'
  
  def __init__(self, stream, endian):
    self._endian = endian
    self._stream = stream
    self._current_word = None
    self._current_word_size = None
    self._num_read = None
    
  def read_bits(self, num):
    pass # @if not self._current_word:

  @classmethod
  def num_bytes_for_bits(clazz, num_bits):
    num_odd_bits = num_bits % 8
    num_bytes = num_bits / 8
    if num_odd_bits > 0:
      num_bytes += 1
    return num_bytes
