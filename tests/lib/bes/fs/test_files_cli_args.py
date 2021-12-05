#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.program_unit_test import program_unit_test

from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.text.text_line_parser import text_line_parser

from test_dir_split import dir_split_tester
from test_file_duplicates import _file_duplicate_tester_base


class _file_duplicate_tester_cli(_file_duplicate_tester_base):

  def __init__(self, ut):
    self._ut = ut
    
  #@abstractmethod
  def find_dups(self, dirs):
    args = [
      'files',
      'dups',
    ] + list(dirs)
    rv = self._ut.run_program(self._ut._program, args)
    return text_line_parser.parse_lines(rv.output, strip_text = True, remove_empties = True)

class test_files_cli_args(program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_split_chunks_of_two(self):
    t = self._split_test([
      dir_split_tester._content('apple', 5),
      dir_split_tester._content('kiwi', 2),
      dir_split_tester._content('lemon', 3),
      dir_split_tester._content('blueberry', 1),
    ], 1, 2)
    expected = [
      'chunk-1/apple1.txt',
      'chunk-1/apple2.txt',
      'chunk-2/apple3.txt',
      'chunk-2/apple4.txt',
      'chunk-3/apple5.txt',
      'chunk-3/blueberry1.txt',
      'chunk-4/kiwi1.txt',
      'chunk-4/kiwi2.txt',
      'chunk-5/lemon1.txt',
      'chunk-5/lemon2.txt',
      'chunk-6/lemon3.txt',
    ]
    self.assertEqual( 0, t.rv.exit_code )
    self.assert_filename_list_equal( expected, t.dst_files )
    self.assert_filename_list_equal( [], t.src_files )

  def test_dups(self):
    self.assertEqual( [
      ( '${_root}/a/lemon.txt', [
        '${_root}/a/lemon_dup.txt',
        '${_root}/b/lemon_dup2.txt',
      ] ),
    ], self._dups_test([ 
      'file a/lemon.txt "this is lemon.txt" 644',
      'file a/kiwi.txt "this is kiwi.txt" 644',
      'file a/lemon_dup.txt "this is lemon.txt" 644',
      'file b/lemon_dup2.txt "this is lemon.txt" 644',
    ], [ 'a', 'b' ]) )

  def test_dups_order(self):
    self.assertEqual( [
      ( '${_root}/b/lemon_dup2.txt', [
        '${_root}/a/lemon.txt',
        '${_root}/a/lemon_dup.txt',
      ] ),
    ], self._dups_test([ 
      'file a/lemon.txt "this is lemon.txt" 644',
      'file a/kiwi.txt "this is kiwi.txt" 644',
      'file a/lemon_dup.txt "this is lemon.txt" 644',
      'file b/lemon_dup2.txt "this is lemon.txt" 644',
    ], [ 'b', 'a' ]) )

  def test_checksums(self):
    self.assertEqual( [
      ( '${_root}/a/lemon.txt', [
        '${_root}/a/lemon_dup.txt',
        '${_root}/b/lemon_dup2.txt',
      ] ),
    ], self._dups_test([ 
      'file a/lemon.txt "this is lemon.txt" 644',
      'file a/kiwi.txt "this is kiwi.txt" 644',
      'file a/lemon_dup.txt "this is lemon.txt" 644',
      'file b/lemon_dup2.txt "this is lemon.txt" 644',
    ], [ 'a', 'b' ]) )
    
  def _split_test(self, content_desc, content_multiplier, chunk_size, extra_content_items = None):
    tmp_dir = dir_split_tester.make_content(content_desc,
                                            content_multiplier,
                                            extra_content_items = extra_content_items)
    src_dir = path.join(tmp_dir, 'src')
    dst_dir = path.join(tmp_dir, 'dst')
    args = [
      'files',
      'split',
      '--prefix', 'chunk-',
      src_dir,
      dst_dir,
      str(chunk_size),
    ]
    src_files_before = file_find.find(src_dir, relative = True, file_type = file_find.ANY)
    rv = self.run_program(self._program, args)
    src_files = file_find.find(src_dir, relative = True)
    dst_files = file_find.find(dst_dir, relative = True)
    return dir_split_tester._test_result(tmp_dir, src_dir, dst_dir, src_files, dst_files, src_files_before, rv)

  def _dups_test(self, items, dirs, extra_dirs_before = [], extra_dirs_after = []):
    tester = _file_duplicate_tester_cli(self)
    return tester.test(items,
                       dirs,
                       extra_dirs_before = extra_dirs_before,
                       extra_dirs_after = extra_dirs_after)
  
if __name__ == '__main__':
  program_unit_test.main()
