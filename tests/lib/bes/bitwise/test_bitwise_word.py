#!/usr/bin/env python3
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.bitwise.bitwise_word import bitwise_word as W

class test_bitwise_word(unit_test):

  def test_get_bit(self):
    self.assert_bit_string_equal( 0, W.get_bit(0b10000000, 0), 8 )
    self.assert_bit_string_equal( 1, W.get_bit(0b00000001, 0), 8 )
    
    self.assert_bit_string_equal( 0, W.get_bit(0xfffffff0, 0), 8 )
    self.assert_bit_string_equal( 1, W.get_bit(0xfffffff1, 0), 8 )
    self.assert_bit_string_equal( 0, W.get_bit(0xfffffff2, 0), 8 )
    self.assert_bit_string_equal( 1, W.get_bit(0x1, 0), 8 )
    self.assert_bit_string_equal( 0, W.get_bit(0x1, 1), 8 )
    self.assert_bit_string_equal( 0, W.get_bit(0x2, 0), 8 )
    self.assert_bit_string_equal( 1, W.get_bit(0x2, 1), 8 )
    self.assert_bit_string_equal( 1, W.get_bit(0x3, 0), 8 )
    self.assert_bit_string_equal( 1, W.get_bit(0x3, 1), 8 )
    self.assert_bit_string_equal( 0, W.get_bit(0x3, 2), 8 )
    
  def test__getitem__(self):
    self.assert_bit_string_equal( 0, W(0b00000000, 8)[0], 8 )
    self.assert_bit_string_equal( 1, W(0b00000001, 8)[0], 8 )
    self.assert_bit_string_equal( 1, W(0b00000010, 8)[1], 8 )
    self.assert_bit_string_equal( 1, W(0b00000100, 8)[2], 8 )
    self.assert_bit_string_equal( 1, W(0b10000100, 8)[7], 8 )

  def test__getitem___slice(self):
    self.assert_bit_string_equal( 0, W(0b00000000, 8)[0:1], 8 )
    self.assert_bit_string_equal( 0b11, W(0b00000011, 8)[0:2], 8 )
    self.assert_bit_string_equal( 0b10, W(0b00000110, 8)[0:2], 8 )
    self.assert_bit_string_equal( 0b110, W(0b00000110, 8)[0:3], 8 )
    self.assert_bit_string_equal( 0b11, W(0b00000110, 8)[1:3], 8 )
    self.assert_bit_string_equal( 0b111, W(0b11110000, 8)[4:7], 8 )
    
  def test_set_bit(self):
    self.assert_bit_string_equal( 0b00000001, W.set_bit(0b00000000, 0, 1), 8 )
    self.assert_bit_string_equal( 0b00000010, W.set_bit(0b00000000, 1, 1), 8 )
    self.assert_bit_string_equal( 0b00000100, W.set_bit(0b00000000, 2, 1), 8 )
    self.assert_bit_string_equal( 0b10000000, W.set_bit(0b00000000, 7, 1), 8 )
    
  def test_set_slice(self):
    self.assert_bit_string_equal( 0b00000001, W.set_slice(0b00000000, 0, 1, 0b1), 8 )
    self.assert_bit_string_equal( 0b00000011, W.set_slice(0b00000000, 0, 2, 0b11), 8 )
    self.assert_bit_string_equal( 0b00000110, W.set_slice(0b00000000, 1, 3, 0b011), 8 )
    self.assert_bit_string_equal( 0b00000110, W.set_slice(0b00000000, 1, 3, 0xffffffff), 8 )
    self.assert_bit_string_equal( 0b10000000, W.set_slice(0b00000000, 7, 8, 0b1), 8 )
    self.assert_bit_string_equal( 0b10000000, W.set_slice(0b00000000, 7, 8, 0b11), 8 )
    self.assert_bit_string_equal( 0b01000000, W.set_slice(0b00000000, 6, 8, 0b101), 8 )
    self.assert_bit_string_equal( 0b01000000, W.set_slice(0b00000000, 6, 8, 0b1), 8 )
    self.assert_bit_string_equal( 0b00100000, W.set_slice(0b00000000, 5, 8, 0b1), 8 )
    
    self.assert_bit_string_equal( 0b00001010, W.set_slice(0b00000000, 0, 4, 0b1010), 8 )
    self.assert_bit_string_equal( 0b00000101, W.set_slice(0b00000000, 0, 4, 0b0101), 8 )
    self.assert_bit_string_equal( 0b00000001, W.set_slice(0b00000000, 0, 4, 0b0001), 8 )
    self.assert_bit_string_equal( 0b00001000, W.set_slice(0b00000000, 0, 4, 0b1000), 8 )

    self.assert_bit_string_equal( 0b11111010, W.set_slice(0b11110000, 0, 4, 0b1010), 8 )
    self.assert_bit_string_equal( 0b11110101, W.set_slice(0b11110000, 0, 4, 0b0101), 8 )
    self.assert_bit_string_equal( 0b11110001, W.set_slice(0b11110000, 0, 4, 0b0001), 8 )
    self.assert_bit_string_equal( 0b11111000, W.set_slice(0b11110000, 0, 4, 0b1000), 8 )
    
if __name__ == "__main__":
  unit_test.main()
