#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.fs.file_util import file_util

from _bes_unit_test_common.dir_operation_tester import dir_operation_tester

class test_files_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_move_files(self):
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
    ]
    t = self._move_files_test(extra_content_items = items,
                              recursive = True)
    dst_after_expected = [
      'a',
      'a/kiwi-10.txt',
      'a/kiwi-20.txt',
      'a/kiwi-30.txt',
      'b',
      'b/lemon-10.txt',
      'b/lemon-20.txt',
      'b/lemon-30.txt',
      'c',
      'c/cheese-10.txt',
      'icons',
      'icons/foo.note',
      'readme.md',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )

  def test_move_files_with_duplicate_file_conflicts(self):
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
      'file dst/readme.md "readme.md" 0644',
      'file dst/icons/foo.note "foo.note" 0644',
    ]
    t = self._move_files_test(extra_content_items = items,
                              recursive = True)
    dst_after_expected = [
      'a',
      'a/kiwi-10.txt',
      'a/kiwi-20.txt',
      'a/kiwi-30.txt',
      'b',
      'b/lemon-10.txt',
      'b/lemon-20.txt',
      'b/lemon-30.txt',
      'c',
      'c/cheese-10.txt',
      'icons',
      'icons/foo.note',
      'readme.md',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )

  def test_move_files_with_non_duplicate_file_conflicts(self):
    items = [
      'file src/readme.md "src readme.md" 0644',
      'file src/a/kiwi-10.txt "kiwi-10.txt" 0644',
      'file src/a/kiwi-20.txt "kiwi-20.txt" 0644',
      'file src/a/kiwi-30.txt "kiwi-30.txt" 0644',
      'file src/b/lemon-10.txt "lemon-10.txt" 0644',
      'file src/b/lemon-20.txt "lemon-20.txt" 0644',
      'file src/b/lemon-30.txt "lemon-30.txt" 0644',
      'file src/c/cheese-10.txt "cheese-10.txt" 0644',
      'file src/icons/foo.note "src foo.note" 0644',
      'file dst/readme.md "dst readme.md" 0644',
      'file dst/icons/foo.note "dst foo.note" 0644',
    ]
    t = self._move_files_test(extra_content_items = items,
                              recursive = True,
                              dup_file_timestamp = 'timestamp',
                              dup_file_count = 1)
    dst_after_expected = [
      'a',
      'a/kiwi-10.txt',
      'a/kiwi-20.txt',
      'a/kiwi-30.txt',
      'b',
      'b/lemon-10.txt',
      'b/lemon-20.txt',
      'b/lemon-30.txt',
      'c',
      'c/cheese-10.txt',
      'icons',
      'icons/foo-timestamp-1.note',
      'icons/foo.note',
      'readme-timestamp-2.md',
      'readme.md',
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )

  def test_move_files_with_dry_run(self):
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
    ]
    t = self._move_files_test(extra_content_items = items,
                              recursive = True,
                              dry_run = True)
    src_after_expected = [
      'a',
      'a/kiwi-10.txt',
      'a/kiwi-20.txt',
      'a/kiwi-30.txt',
      'b',
      'b/lemon-10.txt',
      'b/lemon-20.txt',
      'b/lemon-30.txt',
      'c',
      'c/cheese-10.txt',
      'icons',
      'icons/foo.note',
      'readme.md',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )
    dst_after_expected = [
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )

    self.assert_string_equal_fuzzy(f'''\
DRY_RUN: {t.src_dir}/a/kiwi-10.txt => {t.dst_dir}/a/kiwi-10.txt
DRY_RUN: {t.src_dir}/a/kiwi-20.txt => {t.dst_dir}/a/kiwi-20.txt
DRY_RUN: {t.src_dir}/a/kiwi-30.txt => {t.dst_dir}/a/kiwi-30.txt
DRY_RUN: {t.src_dir}/b/lemon-10.txt => {t.dst_dir}/b/lemon-10.txt
DRY_RUN: {t.src_dir}/b/lemon-20.txt => {t.dst_dir}/b/lemon-20.txt
DRY_RUN: {t.src_dir}/b/lemon-30.txt => {t.dst_dir}/b/lemon-30.txt
DRY_RUN: {t.src_dir}/c/cheese-10.txt => {t.dst_dir}/c/cheese-10.txt
DRY_RUN: {t.src_dir}/icons/foo.note => {t.dst_dir}/icons/foo.note
DRY_RUN: {t.src_dir}/readme.md => {t.dst_dir}/readme.md
''', t.result.output )
    
  def xtest_partition_with_prefix_dry_run(self):
    items = [
      temp_content('file', 'src/readme.md', 'readme.md', 0o0644),
      temp_content('file', 'src/a/kiwi-10.txt', 'kiwi-10.txt', 0o0644),
      temp_content('file', 'src/a/kiwi-20.txt', 'kiwi-20.txt', 0o0644),
      temp_content('file', 'src/a/kiwi-30.txt', 'kiwi-30.txt', 0o0644),
      temp_content('file', 'src/b/lemon-10.txt', 'lemon-10.txt', 0o0644),
      temp_content('file', 'src/b/lemon-20.txt', 'lemon-20.txt', 0o0644),
      temp_content('file', 'src/b/lemon-30.txt', 'lemon-30.txt', 0o0644),
      temp_content('file', 'src/c/cheese-10.txt', 'cheese-10.txt', 0o0644),
      temp_content('file', 'src/icons/foo.note', 'foo.note', 0o0644),
    ]
    t = self._move_files_test(extra_content_items = items,
                              recursive = True,
                              dry_run = True)
    dst_after_expected = [
    ]
    self.assert_filename_list_equal( dst_after_expected, t.dst_files )
    src_after_expected = [
      'a',
      'a/kiwi-10.txt',
      'a/kiwi-20.txt',
      'a/kiwi-30.txt',
      'b',
      'b/lemon-10.txt',
      'b/lemon-20.txt',
      'b/lemon-30.txt',
      'c',
      'c/cheese-10.txt',
      'icons',
      'icons/foo.note',
      'readme.md',
    ]
    self.assert_filename_list_equal( src_after_expected, t.src_files )

    self.assert_string_equal_fuzzy(f'''\
{t.src_dir}/a/kiwi-10.txt => {t.dst_dir}/kiwi/kiwi-10.txt
{t.src_dir}/a/kiwi-20.txt => {t.dst_dir}/kiwi/kiwi-20.txt
{t.src_dir}/a/kiwi-30.txt => {t.dst_dir}/kiwi/kiwi-30.txt 
{t.src_dir}/b/lemon-10.txt => {t.dst_dir}/lemon/lemon-10.txt 
{t.src_dir}/b/lemon-20.txt => {t.dst_dir}/lemon/lemon-20.txt 
{t.src_dir}/b/lemon-30.txt => {t.dst_dir}/lemon/lemon-30.txt 
{t.src_dir}/c/cheese-10.txt => {t.dst_dir}/cheese/cheese-10.txt
''', t.result.output )
    
  def _move_files_test(self,
                       extra_content_items = None,
                       recursive = False,
                       dry_run = False,
                       dup_file_timestamp = None,
                       dup_file_count = None):
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
      if dup_file_timestamp:
        args.extend([ '--dup-file-timestamp', dup_file_timestamp ])
      if dup_file_count:
        args.extend([ '--dup-file-count', str(dup_file_count) ])
      test.result = self.run_program(self._program, args)
    return test

if __name__ == '__main__':
  program_unit_test.main()
