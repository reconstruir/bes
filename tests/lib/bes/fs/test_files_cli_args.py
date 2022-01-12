#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path
from bes.testing.program_unit_test import program_unit_test

from bes.fs.file_util import file_util
from bes.fs.file_find import file_find
from bes.text.text_line_parser import text_line_parser

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
    
  def _dups_test(self, items, dirs, extra_dirs_before = [], extra_dirs_after = []):
    tester = _file_duplicate_tester_cli(self)
    return tester.test(items,
                       dirs,
                       extra_dirs_before = extra_dirs_before,
                       extra_dirs_after = extra_dirs_after)
  
if __name__ == '__main__':
  program_unit_test.main()
