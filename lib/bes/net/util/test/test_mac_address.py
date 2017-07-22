#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest

from bes.net.util import mac_address
from bes.fs import temp_file

class test_mac_address(unittest.TestCase):

  def test_parse_mac_address(self):
    self.assertEqual( [ '00', '11', '22', '33', '44', '55' ], mac_address.parse_mac_address('00:11:22:33:44:55') )
    self.assertEqual( [ 'aa', 'bb', 'cc', 'dd', 'ee', 'ff' ], mac_address.parse_mac_address('aa:bb:cc:dd:ee:ff') )
    self.assertEqual( [ 'AA', 'BB', 'CC', 'DD', 'EE', 'FF' ], mac_address.parse_mac_address('AA:BB:CC:DD:EE:FF') )
    self.assertEqual( [ '0', '1', '2', '3', '4', '5' ], mac_address.parse_mac_address('0:1:2:3:4:5') )
    self.assertEqual( [ 'a', 'b', 'c', 'd', 'e', 'f' ], mac_address.parse_mac_address('a:b:c:d:e:f') )
    self.assertEqual( [ 'A', 'B', 'C', 'D', 'E', 'F' ], mac_address.parse_mac_address('A:B:C:D:E:F') )
    self.assertEqual( [ '00', '11', '22', '33', '44', '55' ], mac_address.parse_mac_address('00-11-22-33-44-55') )
    self.assertEqual( [ 'aa', 'bb', 'cc', 'dd', 'ee', 'ff' ], mac_address.parse_mac_address('aa-bb-cc-dd-ee-ff') )
    self.assertEqual( [ 'AA', 'BB', 'CC', 'DD', 'EE', 'FF' ], mac_address.parse_mac_address('AA-BB-CC-DD-EE-FF') )
    self.assertEqual( [ '0', '1', '2', '3', '4', '5' ], mac_address.parse_mac_address('0-1-2-3-4-5') )
    self.assertEqual( [ 'a', 'b', 'c', 'd', 'e', 'f' ], mac_address.parse_mac_address('a-b-c-d-e-f') )
    self.assertEqual( [ 'A', 'B', 'C', 'D', 'E', 'F' ], mac_address.parse_mac_address('A-B-C-D-E-F') )

  def test_normalize_mac_address(self):
    self.assertEqual( 'aa:bb:cc:dd:ee:ff', mac_address.normalize_mac_address('aa:bb:cc:dd:ee:ff') )
    self.assertEqual( '0a:0b:0c:0d:0e:0f', mac_address.normalize_mac_address ('a:b:c:d:e:f') )
    self.assertEqual( 'aa:bb:cc:dd:ee:ff', mac_address.normalize_mac_address('aa-bb-cc-dd-ee-ff') )
    self.assertEqual( '0a:0b:0c:0d:0e:0f', mac_address.normalize_mac_address ('a-b-c-d-e-f') )
    self.assertEqual( 'aa:bb:cc:dd:ee:ff', mac_address.normalize_mac_address('AA:BB:CC:DD:EE:FF') )
    self.assertEqual( '0a:0b:0c:0d:0e:0f', mac_address.normalize_mac_address ('A:B:C:D:E:F') )
    self.assertEqual( 'aa:bb:cc:dd:ee:ff', mac_address.normalize_mac_address('AA-BB-CC-DD-EE-FF') )
    self.assertEqual( '0a:0b:0c:0d:0e:0f', mac_address.normalize_mac_address ('A-B-C-D-E-F') )

  def test_is_valid(self):
    self.assertTrue( mac_address.is_valid('00:11:22:33:44:55') )
    self.assertTrue( mac_address.is_valid('0:1:2:3:4:5') )
    self.assertFalse( mac_address.is_valid('00:11:22:33:44') )
    self.assertFalse( mac_address.is_valid('xy:11:22:33:44:55') )

if __name__ == "__main__":
  unittest.main()
