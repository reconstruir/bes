#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.fs.testing.temp_content import temp_content

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_bf_file_duplicates_cli(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best2.py')

  def xtest_find_duplicates_basic(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True)
    self.assert_string_equal_fuzzy(f'''\
{t.src_dir}/a/kiwi.jpg:
  {t.src_dir}/b/kiwi_dup1.jpg
  {t.src_dir}/c/kiwi_dup2.jpg
''', t.result.output )

  def xtest_find_duplicates_delete(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             delete = True)
    self.assert_string_equal_fuzzy(f'''\
{t.src_dir}/a/kiwi.jpg:
  {t.src_dir}/b/kiwi_dup1.jpg
  {t.src_dir}/c/kiwi_dup2.jpg
''', t.result.output )

    src_after_expected = [
      'a',
      'a/apple.jpg',
      'a/kiwi.jpg',
      'a/lemon.jpg',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )
    
  def xtest_find_duplicates_delete_with_keep_empty_dirs(self):
    items = [
      temp_content('file', 'src/a/kiwi.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/a/apple.jpg', 'this is apple', 0o0644),
      temp_content('file', 'src/a/lemon.jpg', 'this is lemon', 0o0644),
      temp_content('file', 'src/b/kiwi_dup1.jpg', 'this is kiwi', 0o0644),
      temp_content('file', 'src/c/kiwi_dup2.jpg', 'this is kiwi', 0o0644),
    ]
    t = self._find_dups_test(extra_content_items = items,
                             recursive = True,
                             delete = True,
                             keep_empty_dirs = True)
    self.assert_string_equal_fuzzy(f'''\
{t.src_dir}/a/kiwi.jpg:
  {t.src_dir}/b/kiwi_dup1.jpg
  {t.src_dir}/c/kiwi_dup2.jpg
''', t.result.output )
    
    src_after_expected = [
      'a',
      'a/apple.jpg',
      'a/kiwi.jpg',
      'a/lemon.jpg',
      'b',
      'c',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )
    
  def _find_dups_test(self,
                      extra_content_items = None,
                      recursive = False,
                      small_checksum_size = 1024 * 1024,
                      prefer_prefixes = None,
                      delete = False,
                      keep_empty_dirs = False):
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      args = [
        'file_duplicates',
        'dups',
        test.src_dir,
      ]
#      if recursive:
#        args.append('--recursive')
#      if delete:
#        args.append('--delete')
#      if keep_empty_dirs:
#        args.append('--keep')
      test.result = self.run_program(self._program, args)
    return test

if __name__ == '__main__':
  program_unit_test.main()
