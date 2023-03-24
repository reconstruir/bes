#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from bes.testing.unit_test import unit_test
from bes.files.bf_date import bf_date

class test_bf_date(unit_test):

  def test_get_modification_date(self):
    ago = datetime.now() - timedelta(minutes = 42)
    tmp = self.make_temp_file()
    m1 = bf_date.get_modification_date(tmp)
    bf_date.set_modification_date(tmp, ago)
    self.assertEqual( ago, bf_date.get_modification_date(tmp) )
    self.assertNotEqual( m1, bf_date.get_modification_date(tmp) )
  
if __name__ == '__main__':
  unit_test.main()
