#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.testing.program_unit_test import program_unit_test
from bes.files.bf_file_ops import bf_file_ops

from _test_simple_lexer_mixin import _test_simple_lexer_mixin
from _test_simple_parser_mixin import _test_simple_parser_mixin

class test_btl_cli_args(_test_simple_lexer_mixin, _test_simple_parser_mixin, program_unit_test):

  _program = program_unit_test.resolve_program(__file__, '../../../../bin/best.py')

  def test_lexer_make_mmd(self):
    tmp = self.make_temp_file(suffix = '.mmd')
    args = [
      'btl',
      'lexer_make_mmd',
      self._simple_lexer_desc_filename,
      tmp,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    self.assert_text_file_equal_fuzzy( '''
stateDiagram-v2
  direction LR
    
  %% s_start state
  [*] --> s_start
  s_start --> s_done: c_eos
  s_start --> s_start: c_line_break
  s_start --> s_start: c_ws
  s_start --> s_key: c_keyval_key_first
  s_start --> s_done: default

  %% s_key state
  s_key --> s_key: c_keyval_key
  s_key --> s_value: c_key_value_delimiter
  s_key --> s_done: c_eos
    
  %% s_value state
  s_value --> s_start: c_line_break
  s_value --> s_done: c_eos
  s_value --> s_value: default
    
  %% s_done state
  s_done --> [*]    
  ''', tmp )

  def test_lexer_make_diagram(self):
    tmp = self.make_temp_file(suffix = '.svg')
    args = [
      'btl',
      'lexer_make_diagram',
      '--format', 'svg',
      self._simple_lexer_desc_filename,
      tmp,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    #print(bf_file_ops.read(tmp, encoding = 'utf-8'), flush = True)
    #return
    self.assertEqual( True, bf_file_ops.read(tmp, encoding = 'utf-8').startswith('<svg id="mermaid-svg" width="100%" xmlns="http://www.w3.org/2000/svg" class="statediagram"') )
    
  def test_parser_make_mmd(self):
    tmp = self.make_temp_file(suffix = '.mmd')
    args = [
      'btl',
      'parser_make_mmd',
      self._simple_parser_desc_filename,
      tmp,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)

    #print(bf_file_ops.read(tmp, encoding = 'utf-8'), flush = True)
    #return
    
    self.assert_text_file_equal_fuzzy( '''
stateDiagram-v2
  direction LR

  %% s_start state
  [*] --> s_start
  s_start --> s_done: t_done
  s_start --> s_start: t_line_break
  s_start --> s_start: t_space
  s_start --> s_expecting_delimiter: t_key
  s_start --> s_start: t_comment
  s_start --> s_done: default

  %% s_expecting_delimiter state
  s_expecting_delimiter --> s_expecting_value: t_key_value_delimiter
  s_expecting_delimiter --> s_expecting_delimiter: t_space
  s_expecting_delimiter --> s_done: default

  %% s_expecting_value state
  s_expecting_value --> s_after_value: t_value
  s_expecting_value --> s_expecting_value: t_space
  s_expecting_value --> s_done: default

  %% s_after_value state
  s_after_value --> s_done: t_done
  s_after_value --> s_after_value: t_space
  s_after_value --> s_after_value: t_comment
  s_after_value --> s_start: t_line_break
  s_after_value --> s_done: default

  %% s_done state
  s_done --> [*]
  ''', tmp )

  def test_parser_make_diagram(self):
    tmp = self.make_temp_file(suffix = '.svg')
    args = [
      'btl',
      'parser_make_diagram',
      '--format', 'svg',
      self._simple_parser_desc_filename,
      tmp,
    ]
    rv = self.run_program(self._program, args)
    self.assertEqual(0, rv.exit_code)
    #print(bf_file_ops.read(tmp, encoding = 'utf-8'), flush = True)
    #return
    self.assertEqual( True, bf_file_ops.read(tmp, encoding = 'utf-8').startswith('<svg id="mermaid-svg" width="100%" xmlns="http://www.w3.org/2000/svg" class="statediagram"') )
    
if __name__ == '__main__':
  program_unit_test.main()
