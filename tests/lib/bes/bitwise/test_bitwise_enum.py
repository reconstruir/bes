#!/usr/bin/env python#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from io import BytesIO
from bes.testing.unit_test import unit_test
from bes.bitwise.bitwise_enum import bitwise_enum
from bes.bitwise.bitwise_io import bitwise_io

from enum import IntEnum

class fruit(IntEnum):
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
    f = bitwise_enum(fruit, 1, fruit.DEFAULT)
    f.read_from_io(bitwise_io(BytesIO(buf.getvalue())))
    self.assertEqual( fruit['KIWI'], f.value )
    
  def test_write(self):
    buf = BytesIO()
    io = bitwise_io(buf)
    f = bitwise_enum(fruit, 1, fruit.KIWI)
    f.write_to_io(io)
    self.assertEqual( fruit.KIWI, bitwise_io(BytesIO(buf.getvalue())).read_u8() )
    
if __name__ == "__main__":
  unit_test.main()
