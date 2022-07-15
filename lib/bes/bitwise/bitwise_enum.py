#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from enum import IntEnum

class bitwise_enum(object):

  def __init__(self, enum_class, size, value):
    if not issubclass(enum_class, IntEnum):
      raise TypeError('enum_class should be a subclass of IntEnum: {}'.format(enum_class))
    self._enum_class = enum_class

    check.check_int(size)
    self._size = size

    if check.is_int(value):
      value = self._enum_class(value)
    elif check.is_string(value):
      value = self._enum_class[value]
    self.value = value
    
  def write_to_io(self, io):
    io.write(self.value.value, self._size)
    
  def read_from_io(self, io):
    value = io.read(self._size)
    self.value = self._enum_class(value)
