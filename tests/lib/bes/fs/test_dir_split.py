#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from bes.fs.dir_split import dir_split
from bes.fs.dir_split_options import dir_split_options
from bes.fs.testing.temp_content import temp_content
from bes.fs.testing.temp_content import multiplied_temp_content
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files
from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_dir_split(unit_test, unit_test_media_files):

  def test_split_chunks_of_two(self):
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 2)
    expected = [
      'chunk-1',
      'chunk-1/apple1.txt',
      'chunk-1/apple2.txt',
      'chunk-2',
      'chunk-2/apple3.txt',
      'chunk-2/apple4.txt',
      'chunk-3',
      'chunk-3/apple5.txt',
      'chunk-3/blueberry1.txt',
      'chunk-4',
      'chunk-4/kiwi1.txt',
      'chunk-4/kiwi2.txt',
      'chunk-5',
      'chunk-5/lemon1.txt',
      'chunk-5/lemon2.txt',
      'chunk-6',
      'chunk-6/lemon3.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_split_chunks_of_one(self):
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 1)
    expected = [
      'chunk-01',
      'chunk-01/apple1.txt',
      'chunk-02',
      'chunk-02/apple2.txt',
      'chunk-03',
      'chunk-03/apple3.txt',
      'chunk-04',
      'chunk-04/apple4.txt',
      'chunk-05',
      'chunk-05/apple5.txt',
      'chunk-06',
      'chunk-06/blueberry1.txt',
      'chunk-07',
      'chunk-07/kiwi1.txt',
      'chunk-08',
      'chunk-08/kiwi2.txt',
      'chunk-09',
      'chunk-09/lemon1.txt',
      'chunk-10',
      'chunk-10/lemon2.txt',
      'chunk-11',
      'chunk-11/lemon3.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_split_one_chunk(self):
    t = self._split_test([
      multiplied_temp_content('apple', 1),
      multiplied_temp_content('kiwi', 1),
    ], 1, 3)
    expected = [
      'chunk-1',
      'chunk-1/apple1.txt',
      'chunk-1/kiwi1.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )
    
  def test_split_larger_dir(self):
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 3, 3)
    expected = [
      'chunk-01',
      'chunk-01/apple1.txt',
      'chunk-01/apple10.txt',
      'chunk-01/apple11.txt',
      'chunk-02',
      'chunk-02/apple12.txt',
      'chunk-02/apple13.txt',
      'chunk-02/apple14.txt',
      'chunk-03',
      'chunk-03/apple15.txt',
      'chunk-03/apple2.txt',
      'chunk-03/apple3.txt',
      'chunk-04',
      'chunk-04/apple4.txt',
      'chunk-04/apple5.txt',
      'chunk-04/apple6.txt',
      'chunk-05',
      'chunk-05/apple7.txt',
      'chunk-05/apple8.txt',
      'chunk-05/apple9.txt',
      'chunk-06',
      'chunk-06/blueberry1.txt',
      'chunk-06/blueberry2.txt',
      'chunk-06/blueberry3.txt',
      'chunk-07',
      'chunk-07/kiwi1.txt',
      'chunk-07/kiwi2.txt',
      'chunk-07/kiwi3.txt',
      'chunk-08',
      'chunk-08/kiwi4.txt',
      'chunk-08/kiwi5.txt',
      'chunk-08/kiwi6.txt',
      'chunk-09',
      'chunk-09/lemon1.txt',
      'chunk-09/lemon2.txt',
      'chunk-09/lemon3.txt',
      'chunk-10',
      'chunk-10/lemon4.txt',
      'chunk-10/lemon5.txt',
      'chunk-10/lemon6.txt',
      'chunk-11',
      'chunk-11/lemon7.txt',
      'chunk-11/lemon8.txt',
      'chunk-11/lemon9.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_split_existing_dst(self):
    extra_content_items = [
      'file dst/chunk-1/existing1.txt "this is existing1.txt" 644',
      'file dst/chunk-1/existing2.txt "this is existing2.txt" 644',
      'file dst/chunk-2/existing3.txt "this is existing3.txt" 644',
    ]
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 2, extra_content_items = extra_content_items)
    expected = [
      'chunk-1',
      'chunk-1/existing1.txt',
      'chunk-1/existing2.txt',
      'chunk-2',
      'chunk-2/apple1.txt',
      'chunk-2/existing3.txt',
      'chunk-3',
      'chunk-3/apple2.txt',
      'chunk-3/apple3.txt',
      'chunk-4',
      'chunk-4/apple4.txt',
      'chunk-4/apple5.txt',
      'chunk-5',
      'chunk-5/blueberry1.txt',
      'chunk-5/kiwi1.txt',
      'chunk-6',
      'chunk-6/kiwi2.txt',
      'chunk-6/lemon1.txt',
      'chunk-7',
      'chunk-7/lemon2.txt',
      'chunk-7/lemon3.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_split_existing_dst_grow_split_digits(self):
    extra_content_items = [
      'file dst/chunk-1/existing01.txt "this is existing01.txt" 644',
      'file dst/chunk-1/existing02.txt "this is existing02.txt" 644',
      'file dst/chunk-1/existing03.txt "this is existing03.txt" 644',
      'file dst/chunk-1/existing04.txt "this is existing04.txt" 644',
      'file dst/chunk-1/existing05.txt "this is existing05.txt" 644',
      'file dst/chunk-1/existing06.txt "this is existing06.txt" 644',
      'file dst/chunk-1/existing07.txt "this is existing07.txt" 644',
      'file dst/chunk-1/existing08.txt "this is existing08.txt" 644',
      'file dst/chunk-1/existing09.txt "this is existing09.txt" 644',
      'file dst/chunk-1/existing10.txt "this is existing01.txt" 644',
    ]
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 2, extra_content_items = extra_content_items)
    expected = [
      'chunk-01',
      'chunk-01/existing01.txt',
      'chunk-01/existing02.txt',
      'chunk-02',
      'chunk-02/existing03.txt',
      'chunk-02/existing04.txt',
      'chunk-03',
      'chunk-03/existing05.txt',
      'chunk-03/existing06.txt',
      'chunk-04',
      'chunk-04/existing07.txt',
      'chunk-04/existing08.txt',
      'chunk-05',
      'chunk-05/existing09.txt',
      'chunk-05/existing10.txt',
      'chunk-06',
      'chunk-06/apple1.txt',
      'chunk-06/apple2.txt',
      'chunk-07',
      'chunk-07/apple3.txt',
      'chunk-07/apple4.txt',
      'chunk-08',
      'chunk-08/apple5.txt',
      'chunk-08/blueberry1.txt',
      'chunk-09',
      'chunk-09/kiwi1.txt',
      'chunk-09/kiwi2.txt',
      'chunk-10',
      'chunk-10/lemon1.txt',
      'chunk-10/lemon2.txt',
      'chunk-11',
      'chunk-11/lemon3.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_split_unrelated_src_dirs(self):
    extra_content_items = [
      'file src/unrelated-1/foo.txt "this is foo.txt" 644',
      'file src/unrelated-2/bar.txt "this is bar.txt" 644',
    ]
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 2, extra_content_items = extra_content_items)
    expected = [
      'chunk-1',
      'chunk-1/apple1.txt',
      'chunk-1/apple2.txt',
      'chunk-2',
      'chunk-2/apple3.txt',
      'chunk-2/apple4.txt',
      'chunk-3',
      'chunk-3/apple5.txt',
      'chunk-3/blueberry1.txt',
      'chunk-4',
      'chunk-4/kiwi1.txt',
      'chunk-4/kiwi2.txt',
      'chunk-5',
      'chunk-5/lemon1.txt',
      'chunk-5/lemon2.txt',
      'chunk-6',
      'chunk-6/lemon3.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    expected = [
      'unrelated-1',
      'unrelated-1/foo.txt',
      'unrelated-2',
      'unrelated-2/bar.txt',
    ]
    self.assert_filename_list_equal( expected, t.src_files )

  def test_split_dst_dir_same_as_src(self):
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 2, dst_dir_same_as_src = True)
    expected = [
      'chunk-1',
      'chunk-1/apple1.txt',
      'chunk-1/apple2.txt',
      'chunk-2',
      'chunk-2/apple3.txt',
      'chunk-2/apple4.txt',
      'chunk-3',
      'chunk-3/apple5.txt',
      'chunk-3/blueberry1.txt',
      'chunk-4',
      'chunk-4/kiwi1.txt',
      'chunk-4/kiwi2.txt',
      'chunk-5',
      'chunk-5/lemon1.txt',
      'chunk-5/lemon2.txt',
      'chunk-6',
      'chunk-6/lemon3.txt',
    ]
    self.assert_filename_equal( t.dst_dir, t.src_dir )
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( expected, t.src_files )

  def test_split_recursive(self):
    extra_content_items = [
      'file src/more-1/more-1-foo-1.txt "this is more-1-foo-1.txt" 644',
      'file src/more-1/more-1-foo-2.txt "this is more-1-foo-2.txt" 644',
      'file src/more-1/more-1-foo-3.txt "this is more-1-foo-3.txt" 644',
      'file src/more-2/more-2-bar-1.txt "this is more-2-bar-1.txt" 644',
      'file src/more-2/more-2-bar-2.txt "this is more-2-bar-2.txt" 644',
      'file src/more-3/sub1/more-3-sub1-bar-1.txt "this is more-3-sub1-bar-1.txt" 644',
      'file src/more-3/sub1/more-3-sub1-bar-2.txt "this is more-3-sub1-bar-2.txt" 644',
      'file src/more-3/sub1/more-3-sub2-bar-1.txt "this is more-3-sub2-bar-1.txt" 644',
      'file src/more-3/sub1/more-3-sub2-bar-2.txt "this is more-3-sub2-bar-2.txt" 644',
      'file src/more-3/sub1/sub2/more-3-sub12-bar-1.txt "this is more-3-sub12-bar-1.txt" 644',
      'file src/more-3/sub1/sub2/more-3-sub12-bar-2.txt "this is more-3-sub12-bar-2.txt" 644',
    ]
    t = self._split_test([
      multiplied_temp_content('apple', 5),
      multiplied_temp_content('kiwi', 2),
      multiplied_temp_content('lemon', 3),
      multiplied_temp_content('blueberry', 1),
    ], 1, 2, extra_content_items = extra_content_items, recursive = True)
    expected = [
      'chunk-01',
      'chunk-01/apple1.txt',
      'chunk-01/apple2.txt',
      'chunk-02',
      'chunk-02/apple3.txt',
      'chunk-02/apple4.txt',
      'chunk-03',
      'chunk-03/apple5.txt',
      'chunk-03/blueberry1.txt',
      'chunk-04',
      'chunk-04/kiwi1.txt',
      'chunk-04/kiwi2.txt',
      'chunk-05',
      'chunk-05/lemon1.txt',
      'chunk-05/lemon2.txt',
      'chunk-06',
      'chunk-06/lemon3.txt',
      'chunk-06/more-1-foo-1.txt',
      'chunk-07',
      'chunk-07/more-1-foo-2.txt',
      'chunk-07/more-1-foo-3.txt',
      'chunk-08',
      'chunk-08/more-2-bar-1.txt',
      'chunk-08/more-2-bar-2.txt',
      'chunk-09',
      'chunk-09/more-3-sub1-bar-1.txt',
      'chunk-09/more-3-sub1-bar-2.txt',
      'chunk-10',
      'chunk-10/more-3-sub2-bar-1.txt',
      'chunk-10/more-3-sub2-bar-2.txt',
      'chunk-11',
      'chunk-11/more-3-sub12-bar-1.txt',
      'chunk-11/more-3-sub12-bar-2.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_split_recursive_duplicate_filenames(self):
    extra_content_items = [
      'file src/foo.txt "this is foo.txt 1" 644',
      'file src/sub1/foo.txt "this is sub1/foo.txt" 644',
      'file src/sub2/foo.txt "this is sub2/foo.txt" 644',
    ]
    t = self._split_test([], 1, 3, extra_content_items = extra_content_items, recursive = True)
    expected = [
      'chunk-1',
      'chunk-1/dup-timestamp-1-foo.txt',
      'chunk-1/dup-timestamp-2-foo.txt',
      'chunk-1/foo.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_sort_order(self):
    t = self._split_test([
      multiplied_temp_content('apple', 1, size = 100),
      multiplied_temp_content('kiwi', 1, size = 200),
      multiplied_temp_content('lemon', 1, size = 300),
      multiplied_temp_content('blueberry', 1, size = 400),
      multiplied_temp_content('watermelon', 1, size = 500),
      multiplied_temp_content('grapefruit', 1, size = 600),
    ], 1, 2, sort_order = 'size', sort_reverse = False)
    expected = [
      'chunk-1',
      'chunk-1/apple1.txt',
      'chunk-1/kiwi1.txt',
      'chunk-2',
      'chunk-2/blueberry1.txt',
      'chunk-2/lemon1.txt',
      'chunk-3',
      'chunk-3/grapefruit1.txt',
      'chunk-3/watermelon1.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_sort_order_reverse(self):
    t = self._split_test([
      multiplied_temp_content('apple', 1, size = 100),
      multiplied_temp_content('kiwi', 1, size = 200),
      multiplied_temp_content('lemon', 1, size = 300),
      multiplied_temp_content('blueberry', 1, size = 400),
      multiplied_temp_content('watermelon', 1, size = 500),
      multiplied_temp_content('grapefruit', 1, size = 600),
    ], 1, 2, sort_order = 'size', sort_reverse = True)
    expected = [
      'chunk-1',
      'chunk-1/grapefruit1.txt',
      'chunk-1/watermelon1.txt',
      'chunk-2',
      'chunk-2/blueberry1.txt',
      'chunk-2/lemon1.txt',
      'chunk-3',
      'chunk-3/apple1.txt',
      'chunk-3/kiwi1.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_one_file(self):
    extra_content_items = [
      temp_content('file', 'src/foo.txt', b'this is foo.txt', 0o0644),
    ]
    t = self._split_test([], 1, 1, extra_content_items = extra_content_items, recursive = True)
    expected = [
      'chunk-1',
      'chunk-1/foo.txt',
    ]
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )
    
  def _split_test(self,
                  multiplied_content_items,
                  content_multiplier,
                  chunk_size,
                  extra_content_items = None,
                  dst_dir_same_as_src = False,
                  recursive = False,
                  sort_order = 'filename',
                  sort_reverse = False):
    options = dir_split_options(chunk_size = chunk_size,
                                prefix = 'chunk-',
                                recursive = recursive,
                                dup_file_timestamp = 'dup-timestamp',
                                sort_order = sort_order,
                                sort_reverse = sort_reverse)

    with dir_operation_tester(multiplied_content_items = multiplied_content_items,
                              content_multiplier = content_multiplier,
                              extra_content_items = extra_content_items,
                              dst_dir_same_as_src = dst_dir_same_as_src) as test:
      dir_split.split(test.src_dir, test.dst_dir, options)
    return test
    
if __name__ == '__main__':
  unit_test.main()
