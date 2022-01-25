#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta

from bes.fs.file_path import file_path
from bes.fs.file_poto import file_poto
from bes.fs.file_poto_options import file_poto_options
from bes.fs.file_util import file_util
from bes.fs.testing.temp_content import temp_content
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_file_poto(unit_test):

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

  def test_find_duplicates_with_sort_key(self):
    items = [
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/z/kiwi.jpg', 'this is kiwi', 0o0644),
    ]
    sort_key = lambda filename: 0 if 'z' in file_path.split(filename) else 1
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             sort_key = sort_key)
    self.assertEqual( [
      ( f'{t.src_dir}/z/kiwi.jpg', [
        f'{t.src_dir}/b/kiwi_dup1.jpg',
        f'{t.src_dir}/c/kiwi_dup2.jpg',
      ] ),
    ], t.result.items )

  def test_find_duplicates_with_sort_key_basename_length(self):
    items = [
      temp_content('file', 'src/a/kiwi_12345.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_1234.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_123.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             sort_key = file_poto_options.sort_key_basename_length)
    self.assertEqual( [
      ( f'{t.src_dir}/c/kiwi_123.jpg', [
        f'{t.src_dir}/b/kiwi_1234.jpg',
        f'{t.src_dir}/a/kiwi_12345.jpg',
      ] ),
    ], t.result.items )

  def test_find_duplicates_with_sort_key_modification_date(self):
    items = [
      temp_content('file', 'src/a/kiwi_03.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/b/kiwi_02.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_01.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
    ]
    def _ptf(test):
      file_util.set_modification_date(f'{test.src_dir}/c/kiwi_01.jpg',
                                      datetime.now())
      file_util.set_modification_date(f'{test.src_dir}/b/kiwi_02.jpg',
                                      datetime.now() - timedelta(days = 1))
      file_util.set_modification_date(f'{test.src_dir}/a/kiwi_03.jpg',
                                      datetime.now() - timedelta(days = 2))
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             sort_key = file_poto_options.sort_key_modification_date,
                             pre_test_function = _ptf)
    self.assertEqual( [
      ( f'{t.src_dir}/a/kiwi_03.jpg', [
        f'{t.src_dir}/b/kiwi_02.jpg',
        f'{t.src_dir}/c/kiwi_01.jpg',
      ] ),
    ], t.result.items )

  # FIXME: this test would prove the dups thing works
  # even with no write permissions for files
  @unit_test_function_skip.skip_if_not_unix()
  def xtest_find_duplicates_no_write_permission(self):
    if host.is_linux():
      shell = 'dash'
    else:
      shell = 'sh'
      
    sh_exe = which.which(shell)
    bin_dir = path.dirname(sh_exe)
    tmp_dir = self.make_temp_dir()
    sh_exe_dup = path.join(tmp_dir, 'dupsh.exe')
    file_util.copy(sh_exe, sh_exe_dup)
    result = self._test([ 
    ], [], extra_dirs_before = [
      _file_duplicate_tester_object._extra_dir(bin_dir, '${_bin}'),
      _file_duplicate_tester_object._extra_dir(tmp_dir, '${_tmp}'),
    ] )
    self.assertTrue( file_poto._dup_item('${{_bin}}/{}'.format(shell), [ '${_tmp}/dupsh.exe']) in result )
    
  def _find_dups_test(self,
                      extra_content_items = None,
                      recursive = False,
                      small_checksum_size = 1024 * 1024,
                      prefer_prefixes = None,
                      sort_key = None,
                      pre_test_function = None):
    options = file_poto_options(recursive = recursive,
                                small_checksum_size = small_checksum_size,
                                sort_key = sort_key)
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      if pre_test_function:
        pre_test_function(test)
      if prefer_prefixes:
        xglobals = { 'test': test }
        prefer_prefixes = [ eval(x, xglobals) for x in prefer_prefixes ]
        options.prefer_prefixes = prefer_prefixes
      test.result = file_poto.find_duplicates([ test.src_dir ],
                                              options = options)
    return test
    
if __name__ == '__main__':
  unit_test.main()
