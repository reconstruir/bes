#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.fs.testing.temp_content import temp_content
from bes.fs.file_util import file_util

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_files_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_move_files(self):
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
    t = self._move_files_test(extra_content_items = items,
                             recursive = True)
    dst_after_expected = [
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
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )

  def xtest_partition_with_prefix_dry_run(self):
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
    t = self._move_files_test(extra_content_items = items,
                             recursive = True,
                             dry_run = True)
    dst_after_expected = [
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

    self.assert_string_equal_fuzzy(f'''\
{t.src_dir}/a/kiwi-10.jpg => {t.dst_dir}/kiwi/kiwi-10.jpg
{t.src_dir}/a/kiwi-20.jpg => {t.dst_dir}/kiwi/kiwi-20.jpg
{t.src_dir}/a/kiwi-30.jpg => {t.dst_dir}/kiwi/kiwi-30.jpg 
{t.src_dir}/b/lemon-10.jpg => {t.dst_dir}/lemon/lemon-10.jpg 
{t.src_dir}/b/lemon-20.jpg => {t.dst_dir}/lemon/lemon-20.jpg 
{t.src_dir}/b/lemon-30.jpg => {t.dst_dir}/lemon/lemon-30.jpg 
{t.src_dir}/c/cheese-10.jpg => {t.dst_dir}/cheese/cheese-10.jpg
''', t.result.output )
    
  def _move_files_test(self,
                       extra_content_items = None,
                       recursive = False,
                       dry_run = False):
    with dir_operation_tester(extra_content_items = extra_content_items) as test:
      file_util.mkdir(test.dst_dir)
      args = [
        'files',
        'move',
        test.src_dir,
        test.dst_dir,
      ]
      if recursive:
        args.append('--recursive')
      if dry_run:
        args.append('--dry-run')
      test.result = self.run_program(self._program, args)
    return test

if __name__ == '__main__':
  program_unit_test.main()
