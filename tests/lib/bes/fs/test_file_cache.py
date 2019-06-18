#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.unit_test import unit_test
from bes.fs.file_cache import file_cache
from bes.fs.file_util import file_util
from bes.fs.temp_file import temp_file

class test_file_cache(unit_test):

  def test_cached_filename(self):
    tmp_cache_dir = self.make_temp_dir(prefix = 'test_cached_root_', suffix = '.dir')
    tmp_filename = self.make_temp_file(content = 'foo\n')
    expected_content = file_util.read(tmp_filename)
    cached_filename = file_cache.cached_filename(tmp_filename, cache_dir = tmp_cache_dir)
    print('cached_filename: {}'.format(cached_filename))
    assert False
    return
    actual_content = file_util.read(cached_filename)

    self.assertEqual( expected_content, actual_content )
    self.assertNotEqual( tmp_filename, cached_filename )

  def xtest_cached_content(self):
    tmp_cache_dir = self.make_temp_dir(prefix = 'test_cached_root_', suffix = '.dir')
    tmp_filename = self.make_temp_file(content = 'foo\n')
    expected_content = file_util.read(tmp_filename)
    actual_content = file_cache.cached_content(tmp_filename, cache_dir = tmp_cache_dir)

    self.assertEqual( expected_content, actual_content )

if __name__ == "__main__":
  unit_test.main()
