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

  def xtest_mask(self):
      
    self.assertEqual( ftype.FILE, ftype.DEFAULT )
    self.assertEqual( ftype.DEVICE|ftype.SOCKET, ftype.parse_mask('DEVICE|SOCKET') )
        
    
if __name__ == '__main__':
  unit_test.main()
