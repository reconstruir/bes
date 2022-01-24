#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.fs.file_path import file_path
from bes.fs.file_poto import file_poto
from bes.fs.file_poto_options import file_poto_options
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test

from _bes_unit_test_common.unit_test_media import unit_test_media
from _bes_unit_test_common.unit_test_media_files import unit_test_media_files
from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_file_poto(unit_test, unit_test_media_files):

  def test_find_duplicates(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True)
    self.assertEqual( [
      ( f'{t.src_dir}/a/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ], t.result.items )

  def test_find_duplicates_with_small_checksum_size(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             small_checksum_size = 4)
    self.assertEqual( [
      ( f'{t.src_dir}/a/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ], t.result.items )

  def test_find_duplicates_correct_order(self):
    items = [
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True)
    self.assertEqual( [
      ( f'{t.src_dir}/b/kiwi_dup1.jpg', [
        f'{t.src_dir}/c/kiwi_dup2.jpg',
        f'{t.src_dir}/z/kiwi.jpg',
      ] ),
    ], t.result.items )

  def test_find_duplicates_with_prefer_prefixes(self):
    items = [
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             prefer_prefixes = [
                               "f'{test.src_dir}/z'",
                             ])
    self.assertEqual( [
      ( f'{t.src_dir}/z/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ], t.result.items )

  def test_find_duplicates_with_prefer_function(self):
    items = [
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi.jpg', 'this is kiwi', 0o0644),
    ]
    prefer_function = lambda filename: 0 if 'z' in file_path.split(filename) else 1
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             prefer_function = prefer_function)
    self.assertEqual( [
      ( f'{t.src_dir}/z/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ], t.result.items )
    
  def _find_dups_test(self,
                      extra_content_items = None,
                      recursive = False,
                      small_checksum_size = 1024 * 1024,
                      prefer_prefixes = None,
                      prefer_function = None):
    options = file_poto_options(recursive = recursive,
                                small_checksum_size = small_checksum_size,
                                prefer_function = prefer_function)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      if prefer_prefixes:
        xglobals = { 'test': test }
        prefer_prefixes = [ eval(x, xglobals) for x in prefer_prefixes ]
        options.prefer_prefixes = prefer_prefixes
      test.result = file_poto.find_duplicates([ test.src_dir ],
                                              options = options)
    return test
    
if __name__ == '__main__':
  unit_test.main()
