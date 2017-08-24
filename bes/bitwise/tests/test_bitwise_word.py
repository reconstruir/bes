#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.test import unit_test_helper
from bes.bitwise import bitwise_word as W

class test_bitwise_word(unit_test_helper):

  def test_get_bit(self):
    self.assertEqual( 0, W.get_bit(0b10000000, 0) )
    self.assertEqual( 1, W.get_bit(0b00000001, 0) )
    
    self.assertEqual( 0, W.get_bit(0xfffffff0, 0) )
    self.assertEqual( 1, W.get_bit(0xfffffff1, 0) )
    self.assertEqual( 0, W.get_bit(0xfffffff2, 0) )
    self.assertEqual( 1, W.get_bit(0x1, 0) )
    self.assertEqual( 0, W.get_bit(0x1, 1) )
    self.assertEqual( 0, W.get_bit(0x2, 0) )
    self.assertEqual( 1, W.get_bit(0x2, 1) )
    self.assertEqual( 1, W.get_bit(0x3, 0) )
    self.assertEqual( 1, W.get_bit(0x3, 1) )
    self.assertEqual( 0, W.get_bit(0x3, 2) )
    
  def test__get_item(self):
    self.assertEqual( 0, W(0b00000000, 8)[0] )
    self.assertEqual( 1, W(0b00000001, 8)[0] )
    self.assertEqual( 1, W(0b00000010, 8)[1] )
    self.assertEqual( 1, W(0b00000100, 8)[2] )
    self.assertEqual( 1, W(0b10000100, 8)[7] )

  def test__get_item_slice(self):
    self.assertEqual( 0, W(0b00000000, 8)[0:1] )
    self.assertEqual( 0b11, W(0b00000011, 8)[0:2] )
    self.assertEqual( 0b10, W(0b00000110, 8)[0:2] )
    self.assertEqual( 0b110, W(0b00000110, 8)[0:3] )
    self.assertEqual( 0b11, W(0b00000110, 8)[1:3] )
#    self.assertEqual( 0b1, W(0b10000000, 8)[6:7] )
#    self.assertEqual( 0b11, W(0b11000000, 8)[5:7] )

    #self.assertEqual( 0xf, W(0b00011110, 8)[3:7] )

    self.assertEqual( 0b111, W(0b11110000, 8)[4:7] )
    
#0b1111
    
if __name__ == "__main__":
  unit_test_helper.main()
