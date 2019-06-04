#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum.enum import enum

class bitwise_enum(enum):

  def write_to_io(self, io):
    io.write(self._value, self.SIZE)
    
  def read_from_io(self, io):
    self.value = io.read(self.SIZE)
