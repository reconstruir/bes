#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import math
import random
import string
from datetime import datetime

from bes.archive.temp_archive import temp_archive
from bes.files.split.bf_split import bf_split
from bes.files.split.bf_split import bf_split
from bes.files.split.bf_split_error import bf_split_error
from bes.files.split.bf_split_options import bf_split_options
from bes.files.bf_file_ops import bf_file_ops
from bes.files.bf_entry import bf_entry
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester
from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files

_DEFAULT_FILE_SPLIT_OPTIONS = bf_split_options()

class test_bf_split(unit_test, unit_test_media_files):

  def test__make_split_filename(self):
    f = bf_split._make_split_filename
    self.assert_filename_equal( '/a/b/kiwi.mp4.001', f('/a/b/kiwi.mp4', '/a/b', 1, 3) )
    self.assert_filename_equal( '/a/b/kiwi.mp4.01', f('/a/b/kiwi.mp4', '/a/b', 1, 2) )
    self.assert_filename_equal( '/a/b/kiwi.mp4.1', f('/a/b/kiwi.mp4', '/a/b', 1, 1) )
    self.assert_filename_equal( '/foo/kiwi.mp4.001', f('/a/b/kiwi.mp4', '/foo', 1, 3) )
  
  def test__is_group_file(self):
    f = bf_split._is_group_file
    self.assertEqual( True, f('foo-128.001', 'foo-128.001', None) )
    self.assertEqual( True, f('foo-128.001', 'foo-128.002', None) )
    self.assertEqual( False, f('foo-128.001', 'foo-127.002', None) )
    self.assertEqual( False, f('foo-128.001', 'foo-128.002.zip', None) )

  def test__is_group_file_with_ignored_extension(self):
    f = bf_split._is_group_file
    self.assertEqual( True, f('foo-128.001', 'foo-128.002.zip', ignore_extensions = ( 'zip', )) )
    
  def test_find_and_unsplit(self):
    items = [
      temp_content('file', 'src/a/foo/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/parts/xfoo.txt.001', 'garbage', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.001', 'foo001', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.002', 'foo002', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003', 'foo003', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.xx4', 'garbage', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003.garbage', 'garbage', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.01', 'lemon01', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.02', 'lemon02', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.03', 'lemon03', 0o0644),
      temp_content('file', 'src/c/noext', 'garbage', 0o0644),
    ]
    t = self._find_and_unsplit_test(extra_content_items = items,
                                    recursive = True)
    self.assertEqual( self.xp_filename_list([
      'a',
      'a/foo',
      'a/foo/kiwi.txt',
      'a/parts',
      'a/parts/foo.txt',
      'a/parts/foo.txt.003.garbage',
      'a/parts/foo.txt.xx4',
      'a/parts/xfoo.txt.001',
      'b',
      'b/icons',
      'b/icons/lemon.jpg',
      'c',
      'c/noext',
    ]), self.xp_filename_list(t.src_files) )
    self.assert_text_file_equal( 'foo001foo002foo003', f'{t.src_dir}/a/parts/foo.txt' )
    self.assert_text_file_equal( 'lemon01lemon02lemon03', f'{t.src_dir}/b/icons/lemon.jpg' )

  def test_find_and_unsplit_incomplete_set(self):
    items = [
      temp_content('file', 'src/a/foo/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.001', 'part001', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003', 'part003', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.01', 'part01', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.02', 'part02', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.03', 'part03', 0o0644),
    ]
    with self.assertRaises(bf_split_error) as ctx:
      self._find_and_unsplit_test(extra_content_items = items,
                                  recursive = True)

  def test_find_and_unsplit_with_check_downloading(self):
    items = [
      temp_content('file', 'src/a/foo/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.001', 'part001', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.002', 'part002', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003', 'part003', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003.part', 'foo', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.01', 'part01', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.02', 'part02', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.03', 'part03', 0o0644),
    ]
    t = self._find_and_unsplit_test(extra_content_items = items,
                                    recursive = True,
                                    check_downloading = True)
    self.assertEqual( self.xp_filename_list([
      'a',
      'a/foo',
      'a/foo/kiwi.txt',
      'a/parts',
      'a/parts/foo.txt.001',
      'a/parts/foo.txt.002',
      'a/parts/foo.txt.003',
      'a/parts/foo.txt.003.part',
      'b',
      'b/icons',
      'b/icons/lemon.jpg',
    ]), self.xp_filename_list(t.src_files) )

  def test_find_and_unsplit_existing_target_same(self):
    items = [
      temp_content('file', 'src/a/foo/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt', 'foo001foo002foo003', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.001', 'foo001', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.002', 'foo002', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003', 'foo003', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.01', 'lemon01', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.02', 'lemon02', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.03', 'lemon03', 0o0644),
    ]
    t = self._find_and_unsplit_test(extra_content_items = items,
                                    recursive = True)
    self.assertEqual( self.xp_filename_list([
      'a',
      'a/foo',
      'a/foo/kiwi.txt',
      'a/parts',
      'a/parts/foo.txt',
      'b',
      'b/icons',
      'b/icons/lemon.jpg',
    ]), self.xp_filename_list(t.src_files) )
    self.assert_text_file_equal( 'foo001foo002foo003', f'{t.src_dir}/a/parts/foo.txt' )
    self.assert_text_file_equal( 'lemon01lemon02lemon03', f'{t.src_dir}/b/icons/lemon.jpg' )

  def test_find_and_unsplit_existing_target_different(self):
    items = [
      temp_content('file', 'src/a/foo/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt', 'different', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.001', 'foo001', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.002', 'foo002', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003', 'foo003', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.01', 'lemon01', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.02', 'lemon02', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.03', 'lemon03', 0o0644),
    ]
    ts = datetime(year = 2000, month = 1, day = 1, hour = 1, second = 1)
    t = self._find_and_unsplit_test(extra_content_items = items,
                                    recursive = True,
                                    existing_file_timestamp = ts)
    self.assertEqual( self.xp_filename_list([
      'a',
      'a/foo',
      'a/foo/kiwi.txt',
      'a/parts',
      'a/parts/foo-20000101010001.txt',
      'a/parts/foo.txt',
      'b',
      'b/icons',
      'b/icons/lemon.jpg',
    ]), self.xp_filename_list(t.src_files) )
    self.assert_text_file_equal( 'foo001foo002foo003', f'{t.src_dir}/a/parts/foo-20000101010001.txt' )
    self.assert_text_file_equal( 'different', f'{t.src_dir}/a/parts/foo.txt' )
    self.assert_text_file_equal( 'lemon01lemon02lemon03', f'{t.src_dir}/b/icons/lemon.jpg' )

  def test_find_and_unsplit_with_ignore_extensions(self):
    items = [
      temp_content('file', 'src/a/foo/kiwi.txt', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.001', 'foo001', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.002.zip', 'foo002', 0o0644),
      temp_content('file', 'src/a/parts/foo.txt.003', 'foo003', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.01', 'lemon01', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.02.foo', 'lemon02', 0o0644),
      temp_content('file', 'src/b/icons/lemon.jpg.03', 'lemon03', 0o0644),
    ]
    t = self._find_and_unsplit_test(extra_content_items = items,
                                    recursive = True,
                                    ignore_extensions = ( 'zip', 'foo' ) )
    self.assertEqual( self.xp_filename_list([
      'a',
      'a/foo',
      'a/foo/kiwi.txt',
      'a/parts',
      'a/parts/foo.txt',
      'b',
      'b/icons',
      'b/icons/lemon.jpg',
    ]), self.xp_filename_list(t.src_files) )
    self.assert_text_file_equal( 'foo001foo002foo003', f'{t.src_dir}/a/parts/foo.txt' )
    self.assert_text_file_equal( 'lemon01lemon02lemon03', f'{t.src_dir}/b/icons/lemon.jpg' )

  def test_find_and_unsplit_with_unzip(self):
    tmp = temp_archive.make_temp_archive([
      temp_archive.item('kiwi.mp4', filename = self.mp4_file),
    ], 'zip')
    tmp_dir = self.make_temp_dir()
    files = bf_split.split_file(tmp, int(bf_entry(tmp).size / 3),
                                  output_directory = tmp_dir,
                                  zfill_length = 3)
    self.assertEqual( 4, len(files) )
    items = [
      temp_content('file', 'src/kiwi.mp4.zip.001', bf_file_ops.read(files[0]), 0o0644),
      temp_content('file', 'src/kiwi.mp4.zip.002', bf_file_ops.read(files[1]), 0o0644),
      temp_content('file', 'src/kiwi.mp4.zip.003', bf_file_ops.read(files[2]), 0o0644),
      temp_content('file', 'src/kiwi.mp4.zip.004', bf_file_ops.read(files[3]), 0o0644),
    ]
    t = self._find_and_unsplit_test(extra_content_items = items,
                                    unzip = True)
    self.assertEqual( self.xp_filename_list([
      'kiwi.mp4',
    ]), self.xp_filename_list(t.src_files) )
    self.assertEqual( True, bf_file_ops.files_are_the_same(f'{t.src_dir}/kiwi.mp4',
                                                         self.mp4_file) )

  def test_find_and_unsplit_with_unzip_and_multiple_members(self):
    tmp = temp_archive.make_temp_archive([
      temp_archive.item('kiwi.mp4', filename = self.mp4_file),
      temp_archive.item('lemon.jpg', filename = self.jpg_file),
    ], 'zip')
    tmp_dir = self.make_temp_dir()
    files = bf_split.split_file(tmp, int(bf_entry(tmp).size / 3),
                                  output_directory = tmp_dir,
                                  zfill_length = 3)
    self.assertEqual( 4, len(files) )
    items = [
      temp_content('file', 'src/kiwi.mp4.zip.001', bf_file_ops.read(files[0]), 0o0644),
      temp_content('file', 'src/kiwi.mp4.zip.002', bf_file_ops.read(files[1]), 0o0644),
      temp_content('file', 'src/kiwi.mp4.zip.003', bf_file_ops.read(files[2]), 0o0644),
      temp_content('file', 'src/kiwi.mp4.zip.004', bf_file_ops.read(files[3]), 0o0644),
    ]
    t = self._find_and_unsplit_test(extra_content_items = items,
                                    unzip = True)
    self.assertEqual( [
      'kiwi.mp4.zip',
    ], t.src_files )
    
  def test_split_file_basic(self):
    NUM_ITEMS = 10
    CONTENT_SIZE = 1024 * 100
    items = []
    for i in range(0, NUM_ITEMS):
      arcname = 'item{}.txt'.format(i)
      item = temp_archive.item(arcname, content = self._make_content(CONTENT_SIZE))
      items.append(item)
    tmp_archive = temp_archive.make_temp_archive(items, 'zip')

    files = bf_split.split_file(tmp_archive, int(math.floor(bf_entry(tmp_archive).size / 1)))
    unsplit_tmp_archive = self.make_temp_file()
    bf_split.unsplit_files(unsplit_tmp_archive, files)
    self.assertEqual( bf_entry(tmp_archive).checksum_sha256, bf_entry(unsplit_tmp_archive).checksum_sha256 )
    bf_file_ops.remove(files)
    
    files = bf_split.split_file(tmp_archive, int(math.floor(bf_entry(tmp_archive).size / 2)))
    unsplit_tmp_archive = self.make_temp_file()
    bf_split.unsplit_files(unsplit_tmp_archive, files)
    self.assertEqual( bf_entry(tmp_archive).checksum_sha256, bf_entry(unsplit_tmp_archive).checksum_sha256 )
    bf_file_ops.remove(files)

    files = bf_split.split_file(tmp_archive, int(math.floor(bf_entry(tmp_archive).size / 3)))
    unsplit_tmp_archive = self.make_temp_file()
    bf_split.unsplit_files(unsplit_tmp_archive, files)
    self.assertEqual( bf_entry(tmp_archive).checksum_sha256, bf_entry(unsplit_tmp_archive).checksum_sha256 )
    bf_file_ops.remove(files)
    
    files = bf_split.split_file(tmp_archive, int(math.floor(bf_entry(tmp_archive).size / 4)))
    unsplit_tmp_archive = self.make_temp_file()
    bf_split.unsplit_files(unsplit_tmp_archive, files)
    self.assertEqual( bf_entry(tmp_archive).checksum_sha256, bf_entry(unsplit_tmp_archive).checksum_sha256 )
    bf_file_ops.remove(files)
    
    files = bf_split.split_file(tmp_archive, int(math.floor(bf_entry(tmp_archive).size / 5)))
    unsplit_tmp_archive = self.make_temp_file()
    bf_split.unsplit_files(unsplit_tmp_archive, files)
    self.assertEqual( bf_entry(tmp_archive).checksum_sha256, bf_entry(unsplit_tmp_archive).checksum_sha256 )
    bf_file_ops.remove(files)

  @classmethod
  def _make_content(clazz, size):
    chars = [ c for c in string.ascii_letters ]
    v = []
    for i in range(0, size):
      i = random.randint(0, (len(chars) - 1))
      v.append(chars[i])
    return ''.join(v)

  def _find_and_unsplit_test(self,
                             extra_content_items = None,
                             recursive = False,
                             check_downloading = _DEFAULT_FILE_SPLIT_OPTIONS.check_downloading,
                             check_modified = _DEFAULT_FILE_SPLIT_OPTIONS.check_modified,
                             check_modified_interval = _DEFAULT_FILE_SPLIT_OPTIONS.check_modified_interval,
                             existing_file_timestamp = None,
                             ignore_extensions = None,
                             files = None,
                             unzip = False):
    options = bf_split_options(recursive = recursive,
                                 check_downloading = check_downloading,
                                 existing_file_timestamp = existing_file_timestamp,
                                 ignore_extensions = ignore_extensions,
                                 unzip = unzip)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      files = files or [ test.src_dir ]
      test.result = bf_split.find_and_unsplit(files, options = options)
    return test

  def test_is_split_filename(self):
    self.assertEqual( True, bf_split.is_split_filename('kiwi.001') )
    self.assertEqual( False, bf_split.is_split_filename('kiwi.jpg') )
    self.assertEqual( True, bf_split.is_split_filename('/tmp/kiwi.001') )
    self.assertEqual( False, bf_split.is_split_filename('/tmp/kiwi.jpg') )
  
if __name__ == '__main__':
  unit_test.main()
