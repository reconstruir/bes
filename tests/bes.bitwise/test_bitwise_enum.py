#!/usr/bin/env python#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bitwise import bitwise_enum, bitwise_io
from io import BytesIO

class fruit(bitwise_enum):
  SIZE = 1

  PEAR = 1
  APPLE = 2
  KIWI = 3
  KIWI_CLONE = KIWI
    
  DEFAULT = PEAR
  
class test_bitwise_enum(unit_test):

  def test_read(self):
    buf = BytesIO()
    io = bitwise_io(buf)
    io.write_u8(fruit.KIWI)
    f = fruit()
    f.read_from_io(bitwise_io(BytesIO(buf.getvalue())))
    self.assertEqual( fruit('KIWI'), f )
    
  def test_write(self):
    buf = BytesIO()
    io = bitwise_io(buf)
    f = fruit(fruit.KIWI)
    f.write_to_io(io)
    self.assertEqual( fruit.KIWI, bitwise_io(BytesIO(buf.getvalue())).read_u8() )
    
if __name__ == "__main__":
  unit_test.main()
