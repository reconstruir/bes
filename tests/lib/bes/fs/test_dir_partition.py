#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from os import path

from bes.fs.dir_partition import dir_partition
from bes.fs.dir_partition_options import dir_partition_options
from bes.fs.file_find import file_find
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files
from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_dir_partition(unit_test, unit_test_media_files):

  def xtest_partition_with_media_type(self):
    extra_content_items = [
      temp_content('file', 'src/apple.jpg', unit_test_media.JPG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/barolo.mp4', unit_test_media.MP4_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/brie.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/chablis.mp4', unit_test_media.MP4_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/cheddar.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/kiwi.jpg', unit_test_media.JPG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/lemon.jpg', unit_test_media.JPG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/malbec.mp4', unit_test_media.MP4_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/swiss.png', unit_test_media.PNG_SMALLEST_POSSIBLE, 0o0644),
      temp_content('file', 'src/yogurt.foo', unit_test_media.UNKNOWN, 0o0644),
      temp_content('file', 'src/zabaglione.foo', unit_test_media.UNKNOWN, 0o0644),
    ]
    t = self._do_test([], 0, 3, extra_content_items = extra_content_items, partition = 'media_type')
    expected = [
      'chunk-1',
      'chunk-1/apple.jpg',
      'chunk-1/brie.png',
      'chunk-1/cheddar.png',
      'chunk-2',
      'chunk-2/kiwi.jpg',
      'chunk-2/lemon.jpg',
      'chunk-2/swiss.png',
      'chunk-3',
      'chunk-3/unknown',
      'chunk-3/unknown/yogurt.foo',
      'chunk-3/unknown/zabaglione.foo',
      'chunk-3/video',
      'chunk-3/video/barolo.mp4',
      'chunk-4',
      'chunk-4/chablis.mp4',
      'chunk-4/malbec.mp4',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )
    
  def test_partition_with_prefix(self):
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
    ]
    t = self._partition_test(extra_content_items = items,
                             dst_dir_same_as_src = False,
                             recursive = False,
                             partition_type = 'prefix')
    for f in t.src_files_before:
      print(f'SRC BEFORE: {f}')
    for f in t.dst_files:
      print(f'DST: {f}')
    for f in t.src_files:
      print(f' SRC AFTER: {f}')
    return
    expected = [
      'chunk-1',
      'chunk-1/apple.jpg',
      'chunk-1/brie.png',
      'chunk-1/cheddar.png',
      'chunk-2',
      'chunk-2/kiwi.jpg',
      'chunk-2/lemon.jpg',
      'chunk-2/swiss.png',
      'chunk-3',
      'chunk-3/unknown',
      'chunk-3/unknown/yogurt.foo',
      'chunk-3/unknown/zabaglione.foo',
      'chunk-3/video',
      'chunk-3/video/barolo.mp4',
      'chunk-4',
      'chunk-4/chablis.mp4',
      'chunk-4/malbec.mp4',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )
    
  def _partition_test(self,
                      extra_content_items = None,
                      dst_dir_same_as_src = False,
                      recursive = False,
                      partition_type = None):
    options = dir_partition_options(recursive = recursive,
                                    dup_file_timestamp = 'dup-timestamp',
                                    partition_type = partition_type)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      test.result = dir_partition.partition(test.src_dir,
                                            test.dst_dir,
                                            options = options)
    return test
    
if __name__ == '__main__':
  unit_test.main()
