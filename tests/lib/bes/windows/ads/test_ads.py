#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test

from bes.windows.ads.ads import ads
from bes.windows.ads.ads_error import ads_error

class test_ads(unit_test):

  def test_check_stream_name(self):
    with self.assertRaises(ads_error) as _:
      ads.check_stream_name('foo:bar')
    self.assertEqual( 'foo', ads.check_stream_name('foo') )
  
  def test_has_stream_false(self):
    tmp = self.make_temp_file()
    self.assertFalse( ads.has_stream(tmp, 'notther') )

  def test_has_stream_true(self):
    tmp = self.make_temp_file()
    ads.write_stream(tmp, 'foo', 'hi'.encode('utf-8') )
    self.assertTrue( ads.has_stream(tmp, 'foo') )
    
  def test_write_and_read_stream(self):
    tmp = self.make_temp_file()
    value = 'hi'.encode('utf-8')
    ads.write_stream(tmp, 'foo', value )
    self.assertEqual( value, ads.read_stream(tmp, 'foo') )

  def test_read_stream_non_existent(self):
    tmp = self.make_temp_file()
    with self.assertRaises(ads_error) as _:
      ads.read_stream(tmp, 'nothtere')

  def test_remove_stream(self):
    tmp = self.make_temp_file()
    self.assertFalse( ads.has_stream(tmp, 'foo') )
    ads.write_stream(tmp, 'foo', 'hi'.encode('utf-8') )
    self.assertTrue( ads.has_stream(tmp, 'foo') )
    ads.remove_stream(tmp, 'foo')
    self.assertFalse( ads.has_stream(tmp, 'foo') )
      
if __name__ == '__main__':
  unit_test.main()
