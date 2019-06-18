#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_type import file_type
from bes.fs.temp_file import temp_file
from bes.testing.unit_test_skip import skip_if_not_unix

class test_file_type(unit_test):
  
  def test_file(self):
    tmp_file = temp_file.make_temp_file()
    self.assertTrue( file_type.matches(tmp_file, file_type.FILE) )

  def test_dir(self):
    tmp_dir = temp_file.make_temp_dir()
    self.assertTrue( file_type.matches(tmp_dir, file_type.DIR) )

  def test_file_or_dir(self):
    tmp_file = temp_file.make_temp_dir()
    tmp_dir = temp_file.make_temp_dir()
    self.assertTrue( file_type.matches(tmp_file, file_type.DIR | file_type.FILE) )
    self.assertTrue( file_type.matches(tmp_dir, file_type.DIR | file_type.FILE) )

  @skip_if_not_unix
  def test_char(self):
    self.assertTrue( file_type.matches('/dev/null', file_type.CHAR) )

if __name__ == '__main__':
  unit_test.main()
