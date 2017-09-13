#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-


from bes.testing.unit_test import unit_test
from bes.fs import file_type, temp_file

class test_file_type(unit_test):
  
  def test_file(self):
    tmp = temp_file.make_temp_file()
    self.assertTrue( file_type.match(tmp, file_type.FILE) )

if __name__ == '__main__':
  unit_test.main()
