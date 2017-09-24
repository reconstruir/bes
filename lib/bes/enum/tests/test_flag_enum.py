#!/usr/bin/env python#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.enum import flag_enum

class ftype(flag_enum):
  FILE = 0x01
  DIR = 0x02
  DEVICE = 0x04
  SOCKET = 0x08
  REGULAR = FILE|DIR
  ANY = FILE|DIR|DEVICE|SOCKET
  
class test_enum(unit_test):

  def test___init__(self):
    self.assertEqual( ftype.DEVICE, ftype(ftype.DEVICE).value )
    self.assertEqual( ftype.DEVICE, ftype('DEVICE').value )
    self.assertEqual( ftype.DEVICE|ftype.SOCKET, ftype(ftype.DEVICE|ftype.SOCKET).value )
    self.assertEqual( ftype.DEVICE|ftype.SOCKET, ftype('DEVICE|SOCKET').value )
  
  def test___str__(self):
    self.assertEqual( 'DEVICE|SOCKET', str(ftype(ftype.DEVICE|ftype.SOCKET)) )
    
  def test_default(self):
    self.assertEqual( ftype.FILE, ftype(ftype.DEFAULT) )
    self.assertEqual( ftype.FILE, ftype('DEFAULT') )
    
  def test_parse(self):
    self.assertEqual( ftype.DEVICE|ftype.SOCKET, ftype.parse('DEVICE|SOCKET') )
    
  def test_parse_invalid(self):
    with self.assertRaises(ValueError) as context:
      ftype.parse('DEVICE|SOCKET|BOMB')
    
  def test_parse_empty(self):
    self.assertEqual( 0, ftype.parse('') )
    
if __name__ == '__main__':
  unit_test.main()
