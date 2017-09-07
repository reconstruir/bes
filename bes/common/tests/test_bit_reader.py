#!/usr/bin/env python
#-*- coding:utf-8 -*-
#

from bes.testing.unit_test import unit_test
#from bes.common import bit_reader

class test_bit_reader(unit_test):

  def xtest_num_bytes_for_bits(self):
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(1) )
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(2) )
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(3) )
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(4) )
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(5) )
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(6) )
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(7) )
    self.assertEqual( 1, bit_reader.num_bytes_for_bits(8) )
    self.assertEqual( 2, bit_reader.num_bytes_for_bits(9) )

if __name__ == '__main__':
  unit_test.main()
