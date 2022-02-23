#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.dir_combine import dir_combine
from bes.fs.dir_combine_options import dir_combine_options
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files
from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_dir_combine(unit_test, unit_test_media_files):

  def test_combine_recursive(self):
    t = self._combine_test([
      'file src/a/kiwi-30.jpg      "kiwi-30.txt"    644',
      'file src/a/lemon-30.jpg     "lemon-30.txt"   644',
      'file src/a/grape-30.jpg     "grape-30.txt"   644',
      'file src/b/brie-30.jpg      "brie-30.txt"    644',
      'file src/b/cheddar-30.jpg   "cheddar-30.txt" 644',
      'file src/b/gouda-30.jpg     "gouda-30.txt"   644',
      'file src/c/barolo-10.jpg    "barolo-10.txt"  644',
      'file src/c/chablis-10.jpg   "chablis-10.txt"  644',
      'file src/d/steak-10.jpg     "steak-10.txt"  644',
    ], recursive = True, files = [ 'a', 'b', 'c', 'd' ])
    expected = [
      'a',
      'a/barolo-10.jpg',
      'a/brie-30.jpg',
      'a/chablis-10.jpg',
      'a/cheddar-30.jpg',
      'a/gouda-30.jpg',
      'a/grape-30.jpg',
      'a/kiwi-30.jpg',
      'a/lemon-30.jpg',
      'a/steak-10.jpg',
    ]
    self.assert_filename_list_equal( expected, t.src_files )
  
  def test_combine(self):
    items = [
      temp_content('file', 'src/readme.md', 'readme.md', 0o0644),
      temp_content('file', 'src/a/kiwi-10.jpg', 'kiwi-10.txt', 0o0644),
      temp_content('file', 'src/a/kiwi-20.jpg', 'kiwi-20.txt', 0o0644),
      temp_content('file', 'src/a/kiwi-30.jpg', 'kiwi-30.txt', 0o0644),
      temp_content('file', 'src/b/lemon-10.jpg', 'lemon-10.txt', 0o0644),
      temp_content('file', 'src/b/lemon-20.jpg', 'lemon-20.txt', 0o0644),
      temp_content('file', 'src/b/lemon-30.jpg', 'lemon-30.txt', 0o0644),
      temp_content('file', 'src/c/cheese-10.jpg', 'cheese-10.jpg', 0o0644),
      temp_content('file', 'src/icons/foo.png', 'foo.png', 0o0644),
      temp_content('file', 'src/kiwi-40.jpg', 'kiwi-40.txt', 0o0644),
      temp_content('file', 'src/kiwi-50.jpg', 'kiwi-50.txt', 0o0644),
      temp_content('file', 'src/lemon-40.jpg', 'lemon-40.txt', 0o0644),
      temp_content('file', 'src/lemon-50.jpg', 'lemon-50.txt', 0o0644),
    ]
    t = self._combine_test(extra_content_items = items,
                           dst_dir_same_as_src = False,
                           recursive = False,
                           partition_type = 'prefix')
    dst_after_expected = [
      'kiwi-40.jpg',
      'kiwi-50.jpg',
      'lemon-40.jpg',
      'lemon-50.jpg',
      'readme.md',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.src_files )

  def test_combine_nothing(self):
    items = [
      temp_content('dir', 'src', '', 0o0700),
    ]
    t = self._combine_test(extra_content_items = items,
                           dst_dir_same_as_src = False,
                           recursive = False,
                           partition_type = 'prefix')
    self.assert_filename_list_equal( [], t.src_files )
    
  def test_combine(self):
    items = [
      temp_content('file', 'src/readme.md', 'readme.md', 0o0644),
      temp_content('file', 'src/a/kiwi-10.jpg', 'kiwi-10.txt', 0o0644),
      temp_content('file', 'src/a/kiwi-20.jpg', 'kiwi-20.txt', 0o0644),
      temp_content('file', 'src/a/kiwi-30.jpg', 'kiwi-30.txt', 0o0644),
      temp_content('file', 'src/b/lemon-10.jpg', 'lemon-10.txt', 0o0644),
      temp_content('file', 'src/b/lemon-20.jpg', 'lemon-20.txt', 0o0644),
      temp_content('file', 'src/b/lemon-30.jpg', 'lemon-30.txt', 0o0644),
      temp_content('file', 'src/c/cheese-10.jpg', 'cheese-10.jpg', 0o0644),
      temp_content('file', 'src/icons/foo.png', 'foo.png', 0o0644),
      temp_content('file', 'src/kiwi-40.jpg', 'kiwi-40.txt', 0o0644),
      temp_content('file', 'src/kiwi-50.jpg', 'kiwi-50.txt', 0o0644),
      temp_content('file', 'src/lemon-40.jpg', 'lemon-40.txt', 0o0644),
      temp_content('file', 'src/lemon-50.jpg', 'lemon-50.txt', 0o0644),
    ]
    t = self._combine_test(extra_content_items = items,
                           dst_dir_same_as_src = False,
                           recursive = False,
                           partition_type = 'prefix',
                           files = [ 'a', 'b' ])
    dst_after_expected = [
      'a',
      'a/kiwi-10.jpg',
      'a/kiwi-20.jpg',
      'a/kiwi-30.jpg',
      'a/lemon-10.jpg',
      'a/lemon-20.jpg',
      'a/lemon-30.jpg',
      'c',
      'c/cheese-10.jpg',
      'icons',
      'icons/foo.png',
      'kiwi-40.jpg',
      'kiwi-50.jpg',
      'lemon-40.jpg',
      'lemon-50.jpg',
      'readme.md',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.src_files )
    
  def _combine_test(self,
                    extra_content_items = None,
                    dst_dir_same_as_src = False,
                    recursive = False,
                    partition_type = None,
                    files = None):
    options = dir_combine_options(recursive = recursive,
                                  dup_file_timestamp = 'dup-timestamp',
                                  partition_type = partition_type)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      if files:
        files = [ path.join(test.src_dir, f) for f in files ]
      else:
        files = [ test.src_dir ]
      test.result = dir_combine.combine(files, options = options)
    return test
    
if __name__ == '__main__':
  unit_test.main()
