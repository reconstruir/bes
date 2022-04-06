#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.dir_combine import dir_combine
from bes.fs.dir_combine_options import dir_combine_options
from bes.testing.unit_test import unit_test
from bes.fs.dir_combine_defaults import dir_combine_defaults

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files
from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_dir_combine(unit_test, unit_test_media_files):

  def test_combine_recursive(self):
    t = self._combine_test([
      'file src/a/kiwi-30.txt      "kiwi-30.txt"    644',
      'file src/a/lemon-30.txt     "lemon-30.txt"   644',
      'file src/a/grape-30.txt     "grape-30.txt"   644',
      'file src/b/brie-30.txt      "brie-30.txt"    644',
      'file src/b/cheddar-30.txt   "cheddar-30.txt" 644',
      'file src/b/gouda-30.txt     "gouda-30.txt"   644',
      'file src/c/barolo-10.txt    "barolo-10.txt"  644',
      'file src/c/chablis-10.txt   "chablis-10.txt"  644',
      'file src/d/steak-10.txt     "steak-10.txt"  644',
    ],
                           recursive = True,
                           files = [ 'a', 'b', 'c', 'd' ],
                           flatten = True)
    expected = [
      'a',
      'a/barolo-10.txt',
      'a/brie-30.txt',
      'a/chablis-10.txt',
      'a/cheddar-30.txt',
      'a/gouda-30.txt',
      'a/grape-30.txt',
      'a/kiwi-30.txt',
      'a/lemon-30.txt',
      'a/steak-10.txt',
    ]
    self.assert_filename_list_equal( expected, t.src_files )
  
  def test_combine(self):
    items = [
      'file src/readme.md "readme.md" 0644',
      'file src/a/kiwi-10.txt "kiwi-10.txt" 0644',
      'file src/a/kiwi-20.txt "kiwi-20.txt" 0644',
      'file src/a/kiwi-30.txt "kiwi-30.txt" 0644',
      'file src/b/lemon-10.txt "lemon-10.txt" 0644',
      'file src/b/lemon-20.txt "lemon-20.txt" 0644',
      'file src/b/lemon-30.txt "lemon-30.txt" 0644',
      'file src/c/cheese-10.txt "cheese-10.txt" 0644',
      'file src/icons/foo.note "foo.note" 0644',
      'file src/kiwi-40.txt "kiwi-40.txt" 0644',
      'file src/kiwi-50.txt "kiwi-50.txt" 0644',
      'file src/lemon-40.txt "lemon-40.txt" 0644',
      'file src/lemon-50.txt "lemon-50.txt" 0644',
    ]
    t = self._combine_test(extra_content_items = items,
                           dst_dir_same_as_src = False,
                           recursive = False,
                           flatten = True)
    dst_after_expected = [
      'kiwi-40.txt',
      'kiwi-50.txt',
      'lemon-40.txt',
      'lemon-50.txt',
      'readme.md',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.src_files )

  def test_combine_nothing(self):
    items = [
      'dir src "" 0700',
    ]
    t = self._combine_test(extra_content_items = items,
                           dst_dir_same_as_src = False,
                           recursive = False,
                           flatten = True)
    self.assert_filename_list_equal( [], t.src_files )
    
  def test_combine(self):
    items = [
      'file src/readme.md "readme.md" 0644',
      'file src/a/kiwi-10.txt "kiwi-10.txt" 0644',
      'file src/a/kiwi-20.txt "kiwi-20.txt" 0644',
      'file src/a/kiwi-30.txt "kiwi-30.txt" 0644',
      'file src/b/lemon-10.txt "lemon-10.txt" 0644',
      'file src/b/lemon-20.txt "lemon-20.txt" 0644',
      'file src/b/lemon-30.txt "lemon-30.txt" 0644',
      'file src/c/cheese-10.txt "cheese-10.txt" 0644',
      'file src/icons/foo.note "foo.note" 0644',
      'file src/kiwi-40.txt "kiwi-40.txt" 0644',
      'file src/kiwi-50.txt "kiwi-50.txt" 0644',
      'file src/lemon-40.txt "lemon-40.txt" 0644',
      'file src/lemon-50.txt "lemon-50.txt" 0644',
    ]
    t = self._combine_test(extra_content_items = items,
                           dst_dir_same_as_src = False,
                           recursive = False,
                           files = [ 'a', 'b' ],
                           flatten = True)
    dst_after_expected = [
      'a',
      'a/kiwi-10.txt',
      'a/kiwi-20.txt',
      'a/kiwi-30.txt',
      'a/lemon-10.txt',
      'a/lemon-20.txt',
      'a/lemon-30.txt',
      'c',
      'c/cheese-10.txt',
      'icons',
      'icons/foo.note',
      'kiwi-40.txt',
      'kiwi-50.txt',
      'lemon-40.txt',
      'lemon-50.txt',
      'readme.md',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.src_files )
    
  def _combine_test(self,
                    extra_content_items = None,
                    dst_dir_same_as_src = False,
                    recursive = False,
                    files = None,
                    flatten = dir_combine_defaults.FLATTEN,
                    delete_empty_dirs = dir_combine_defaults.DELETE_EMPTY_DIRS):
    options = dir_combine_options(recursive = recursive,
                                  dup_file_timestamp = 'dup-timestamp',
                                  flatten = flatten,
                                  delete_empty_dirs = delete_empty_dirs)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      if files:
        files = [ path.join(test.src_dir, f) for f in files ]
      else:
        files = [ test.src_dir ]
      test.result = dir_combine.combine(files, options = options)
    return test
    
if __name__ == '__main__':
  unit_test.main()
