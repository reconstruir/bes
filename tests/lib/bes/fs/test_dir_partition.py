#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.dir_partition import dir_partition
from bes.fs.dir_partition_options import dir_partition_options
from bes.fs.dir_partition_criteria_base import dir_partition_criteria_base
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files
from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_dir_partition(unit_test, unit_test_media_files):

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
      temp_content('file', 'src/kiwi-40.jpg', 'kiwi-40.txt', 0o0644),
      temp_content('file', 'src/kiwi-50.jpg', 'kiwi-50.txt', 0o0644),
      temp_content('file', 'src/lemon-40.jpg', 'lemon-40.txt', 0o0644),
      temp_content('file', 'src/lemon-50.jpg', 'lemon-50.txt', 0o0644),
    ]
    t = self._partition_test(extra_content_items = items,
                             dst_dir_same_as_src = False,
                             recursive = False,
                             partition_type = 'prefix')
    dst_after_expected = [
      'kiwi',
      'kiwi/kiwi-40.jpg',
      'kiwi/kiwi-50.jpg',
      'lemon',
      'lemon/lemon-40.jpg',
      'lemon/lemon-50.jpg',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
      'a',
      'a/kiwi-10.jpg',
      'a/kiwi-20.jpg',
      'a/kiwi-30.jpg',
      'b',
      'b/lemon-10.jpg',
      'b/lemon-20.jpg',
      'b/lemon-30.jpg',
      'c',
      'c/cheese-10.jpg',
      'icons',
      'icons/foo.png',
      'readme.md',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )
  
  def test_partition_with_prefix_recursive(self):
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
      temp_content('file', 'src/lemon-40.jpg', 'lemon-40.txt', 0o0644),
    ]
    t = self._partition_test(extra_content_items = items,
                             dst_dir_same_as_src = False,
                             recursive = True,
                             partition_type = 'prefix')
    dst_after_expected = [
      'kiwi',
      'kiwi/kiwi-10.jpg',
      'kiwi/kiwi-20.jpg',
      'kiwi/kiwi-30.jpg',
      'kiwi/kiwi-40.jpg',
      'lemon',
      'lemon/lemon-10.jpg',
      'lemon/lemon-20.jpg',
      'lemon/lemon-30.jpg',
      'lemon/lemon-40.jpg',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
      'c',
      'c/cheese-10.jpg',
      'icons',
      'icons/foo.png',
      'readme.md',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )

  def test_partition_with_media_type(self):
    items = [
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
    t = self._partition_test(extra_content_items = items,
                             dst_dir_same_as_src = False,
                             recursive = False,
                             partition_type = 'media_type')
    dst_after_expected = [
      'image',
      'image/apple.jpg',
      'image/brie.png',
      'image/cheddar.png',
      'image/kiwi.jpg',
      'image/lemon.jpg',
      'image/swiss.png',
      'video',
      'video/barolo.mp4',
      'video/chablis.mp4',
      'video/malbec.mp4',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
      'yogurt.foo',
      'zabaglione.foo',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )

  def test_partition_with_criteria(self):
    items = [
      temp_content('file', 'src/kiwi/kiwi4.txt', '1234', 0o0644),
      temp_content('file', 'src/kiwi/kiwi5.txt', '12345', 0o0644),
      temp_content('file', 'src/kiwi/kiwi6.txt', '123456', 0o0644),
      temp_content('file', 'src/kiwi/kiwi7.txt', '1234567', 0o0644),
      temp_content('file', 'src/apple/apple4.txt', '1234', 0o0644),
      temp_content('file', 'src/apple/apple5.txt', '12345', 0o0644),
      temp_content('file', 'src/apple/apple6.txt', '123456', 0o0644),
      temp_content('file', 'src/apple/apple7.txt', '1234567', 0o0644),
      temp_content('file', 'src/lemon/lemon1.txt', '1', 0o0644),
      temp_content('file', 'src/lemon/lemon4.txt', '1234', 0o0644),
      temp_content('file', 'src/lemon/lemon5.txt', '12345', 0o0644),
      temp_content('file', 'src/lemon/lemon6.txt', '123456', 0o0644),
      temp_content('file', 'src/lemon/lemon7.txt', '1234567', 0o0644),
      temp_content('file', 'src/melon/melon1.txt', '1', 0o0644),
    ]
    class _criteria(dir_partition_criteria_base):
      def classify(self, filename):
        size = file_util.size(filename)
        if size == 1:
          return None
        return str(size)
    t = self._partition_test(extra_content_items = items,
                             dst_dir_same_as_src = False,
                             recursive = True,
                             partition_type = 'criteria',
                             partition_criteria = _criteria())
    dst_after_expected = [
      '4',
      '4/apple4.txt',
      '4/kiwi4.txt',
      '4/lemon4.txt',
      '5',
      '5/apple5.txt',
      '5/kiwi5.txt',
      '5/lemon5.txt',
      '6',
      '6/apple6.txt',
      '6/kiwi6.txt',
      '6/lemon6.txt',
      '7',
      '7/apple7.txt',
      '7/kiwi7.txt',
      '7/lemon7.txt',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
      'lemon',
      'lemon/lemon1.txt',
      'melon',
      'melon/melon1.txt',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )
    
  def _partition_test(self,
                      extra_content_items = None,
                      dst_dir_same_as_src = False,
                      recursive = False,
                      partition_type = None,
                      partition_criteria = None):
    with dir_operation_tester(extra_content_items = extra_content_items,
                              dst_dir_same_as_src = dst_dir_same_as_src) as test:
      options = dir_partition_options(recursive = recursive,
                                      dup_file_timestamp = 'dup-timestamp',
                                      partition_type = partition_type,
                                      partition_criteria = partition_criteria,
                                      dst_dir = test.dst_dir)
      test.result = dir_partition.partition(test.src_dir, options = options)
    return test
    
if __name__ == '__main__':
  unit_test.main()
