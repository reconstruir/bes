#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs import file_trash, file_util, temp_file
import os.path as path

class test_file_trash(unit_test):

  def test_init(self):
    t = file_trash(temp_file.make_temp_dir())
    
if __name__ == '__main__':
  unit_test.main()
