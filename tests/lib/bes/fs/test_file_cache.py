#!/usr/bin/env python
#-*- coding:utf-8 -*-
#
import unittest
from bes.fs import file_cache, file_util, temp_file

class test_file_cache(unittest.TestCase):

  DEBUG = False
  #DEBUG = True
  
  def test_cached_filename(self):
    tmp_cache_dir = temp_file.make_temp_dir(prefix = 'test_cached_root_', suffix = '.dir', delete = not self.DEBUG)
    tmp_filename = temp_file.make_temp_file(content = 'foo\n', delete = not self.DEBUG)
    if self.DEBUG:
      print("\ntmp_cache_dir: ", tmp_cache_dir)
      print("tmp_filename: ", tmp_filename)
    expected_content = file_util.read(tmp_filename)
    cached_filename = file_cache.cached_filename(tmp_filename, cache_dir = tmp_cache_dir)
    actual_content = file_util.read(cached_filename)

    self.assertEqual( expected_content, actual_content )
    self.assertNotEqual( tmp_filename, cached_filename )

  def test_cached_content(self):
    tmp_cache_dir = temp_file.make_temp_dir(prefix = 'test_cached_root_', suffix = '.dir', delete = not self.DEBUG)
    tmp_filename = temp_file.make_temp_file(content = 'foo\n', delete = not self.DEBUG)
    expected_content = file_util.read(tmp_filename)
    actual_content = file_cache.cached_content(tmp_filename, cache_dir = tmp_cache_dir)

    self.assertEqual( expected_content, actual_content )

if __name__ == "__main__":
  unittest.main()
