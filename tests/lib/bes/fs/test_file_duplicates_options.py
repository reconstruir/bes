#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_duplicates_options import file_duplicates_options
from bes.testing.unit_test import unit_test

class test_file_duplicates(unit_test):

  def test___setattr__sort_key(self):
    options = file_duplicates_options()
    self.assertEqual( file_duplicates_options.mtime_sort_key, options.sort_key )

    options.sort_key = file_duplicates_options.sort_key_basename_length
    self.assertEqual( file_duplicates_options.sort_key_basename_length, options.sort_key )
  
if __name__ == '__main__':
  unit_test.main()
