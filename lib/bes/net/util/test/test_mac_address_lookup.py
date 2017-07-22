#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import os.path as path, unittest

from bes.net.util import mac_address_lookup
from bes.fs import temp_file

class test_mac_address_lookup(unittest.TestCase):

  def test_put(self):
    tmp_dir = temp_file.make_temp_dir()
    tmp_cache = path.join(tmp_dir, 'mac_address.cache')
    
    self.assertEqual( None, mac_address_lookup.get_alias(tmp_cache, 'aa:bb:cc:dd:ee:ff') )
    mac_address_lookup.put_alias(tmp_cache, 'aa:bb:cc:dd:ee:ff', 'foo')
    self.assertEqual( 'foo', mac_address_lookup.get_alias(tmp_cache, 'aa:bb:cc:dd:ee:ff') )
    self.assertEqual( 'foo', mac_address_lookup.get_alias(tmp_cache, 'AA:BB:CC:DD:EE:FF') )

  def test_put_normalized(self):
    tmp_dir = temp_file.make_temp_dir()
    tmp_cache = path.join(tmp_dir, 'mac_address.cache')

    self.assertEqual( None, mac_address_lookup.get_alias(tmp_cache, 'a:b:c:d:e:f') )
    mac_address_lookup.put_alias(tmp_cache, 'a:b:c:d:e:f', 'foo')
    self.assertEqual( 'foo', mac_address_lookup.get_alias(tmp_cache, 'a:b:c:d:e:f') )
    self.assertEqual( 'foo', mac_address_lookup.get_alias(tmp_cache, 'A:B:C:D:E:F') )
    self.assertEqual( 'foo', mac_address_lookup.get_alias(tmp_cache, '0a:0b:0c:0d:0e:0f') )
    self.assertEqual( 'foo', mac_address_lookup.get_alias(tmp_cache, '0A:0B:0C:0D:0E:0F') )

  def test_get_address(self):
    tmp_dir = temp_file.make_temp_dir()
    tmp_cache = path.join(tmp_dir, 'mac_address.cache')

    mac_address_lookup.put_alias(tmp_cache, '0a:0b:0c:0d:0e:0f', 'foo')
    self.assertEqual( '0a:0b:0c:0d:0e:0f', mac_address_lookup.get_address(tmp_cache, 'foo') )
    self.assertEqual( None, mac_address_lookup.get_address(tmp_cache, 'not_there') )

if __name__ == "__main__":
  unittest.main()
