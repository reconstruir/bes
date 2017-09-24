#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
from bes.testing.unit_test import unit_test
from bes.fs import file_match

from refactor import files

class test_files(unit_test):

  __unit_test_data_dir__ = 'test_data/files'
  def test_foo(self):
    pass
    
if __name__ == "__main__":
  unit_test.main()
