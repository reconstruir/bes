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
  
  def test_has_stream(self):
    tmp = self.make_temp_file()
    self.assertFalse( ads.has_stream(tmp, 'notther') )
    
if __name__ == '__main__':
  unit_test.main()
