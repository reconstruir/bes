#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.system.host import host
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.btl.btl_lexer_tester_mixin import btl_lexer_tester_mixin
from bes.btl.btl_lexer_token_list import btl_lexer_token_list
from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_runtime_error import btl_lexer_runtime_error
from bes.btl.btl_function_base import btl_function_base

class _test_lexer(btl_lexer_base):

  class _token:

    T_DONE = 't_done'
    T_KEY = 't_key'
    T_KEY_VALUE_DELIMITER = 't_key_value_delimiter'
    T_LINE_BREAK = 't_line_break'
    T_SPACE = 't_space'
    T_VALUE = 't_value'

  class e_unexpected_char(btl_lexer_runtime_error):
    pass

  class _function_f_handle_eos(btl_function_base):

    def call(self, context, tokens, token_name):
      tokens.append(self.make_token(context, token_name))
      context.buffer_reset()
      tokens.append(self.make_token(context, 't_done'))
  
  class _state_s_start(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_start'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_done'))
      elif self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
        context.buffer_reset()
      elif self.char_in(c, 'c_ws', context):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_space'))
      elif self.char_in(c, 'c_keyval_key_first', context):
        new_state_name = 's_key'
        context.buffer_write(c)
      else:
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_key(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_key'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_keyval_key', context):
        new_state_name = 's_key'
        context.buffer_write(c)
      elif self.char_in(c, 'c_key_value_delimiter', context):
        new_state_name = 's_value'
        tokens.append(self.make_token(context, 't_key'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_key_value_delimiter'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        self.lexer._function_f_handle_eos(self).call(context, tokens, 't_key')
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_value(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_value'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        self.lexer._function_f_handle_eos(self).call(context, tokens, 't_value')
      else:
        new_state_name = 's_value'
        context.buffer_write(c)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_done(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_done'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      
      return self._handle_char_result(new_state_name, tokens)

  def __init__(self, desc_source = None):
    log_tag = f'_test_simple_lexer'
    desc_text = self._DESC_TEXT
    token = self._token
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_key': self._state_s_key(self, log_tag),
      's_value': self._state_s_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, desc_text, token, states, desc_source = desc_source)
  _DESC_TEXT = """
#BTL
#
# Key Value pair lexer
#
lexer
  name: l_simple
  description: A simple key value pair lexer
  version: 1.0
  start_state: s_start
  end_state: s_done

tokens
  t_done
    type_hint: h_done
  t_key_value_delimiter
  t_key
  t_line_break
    type_hint: h_line_break
  t_space
  t_value

errors
  e_unexpected_char: In state "{self.name}" unexpected character: "{c}"

variables
  v_key_value_delimiter: =

chars
  c_keyval_key_first: c_underscore | c_alpha
  c_keyval_key: c_keyval_key_first | c_numeric
  c_key_value_delimiter: ${v_key_value_delimiter}

functions

  f_handle_eos(token_name)
    emit ${token_name}
    buffer reset
    emit t_done

states

  s_start
    c_eos: s_done
      emit t_done
    c_line_break: s_start
      buffer write
      emit t_line_break
      buffer reset
    c_ws: s_start
      emit t_space 
    c_keyval_key_first: s_key
      buffer write
    default: s_done
      error e_unexpected_char
      
  s_key
    c_keyval_key: s_key
      buffer write
    c_key_value_delimiter: s_value
      emit t_key
      buffer reset
      buffer write
      emit t_key_value_delimiter
      buffer reset
    c_eos: s_done
      emit t_key
      buffer reset
      emit t_done
      
  s_value
    c_line_break: s_start
      emit t_value
      buffer reset
      buffer write
      emit t_line_break
      buffer reset
    c_eos: s_done
      emit t_value
      buffer reset
      emit t_done
    default: s_value
      buffer write
      
  s_done

"""

class test_btl_lexer_base(btl_lexer_tester_mixin, unit_test):

  def test_empty_string(self):
    t = self.call_lex_all(_test_lexer, '',
      [
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_just_key(self):
    t = self.call_lex_all(_test_lexer, 'a',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )
    
  def test_just_key_and_equal(self):
    t = self.call_lex_all(_test_lexer, 'ab=',
      [
        ( 't_key', 'ab', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 3 ), None, None ),
        ( 't_value', '', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value_short(self):
    t = self.call_lex_all(_test_lexer, 'a=k',
      [
        ( 't_key', 'a', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
        ( 't_value', 'k', ( 1, 3 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_key_and_value(self):
    t = self.call_lex_all(_test_lexer, 'fruit=kiwi',
      [
        ( 't_key', 'fruit', ( 1, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 1, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 1, 7 ), None, None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_nl(self):
    t = self.call_lex_all(_test_lexer, '''\nfruit=kiwi\ncolor=green\n''',
      [
        ( 't_line_break', '[NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[NL]', (  3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_multi_line_crlf(self):
    t = self.call_lex_all(_test_lexer, '''\r\nfruit=kiwi\r\ncolor=green\r\n''',
      [
        ( 't_line_break', '[CR][NL]', ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', '[CR][NL]', (  2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', '[CR][NL]', (  3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  @unit_test_function_skip.skip_if(not host.is_windows(), 'not windows')
  def test_multi_line_os_linesep_windows(self):
    t = self.call_lex_all(_test_lexer, '''\r\nfruit=kiwi\r\ncolor=green\r\n''',
      [
        ( 't_line_break', os.linesep, ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', os.linesep, (  2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', os.linesep, (  3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  @unit_test_function_skip.skip_if(not host.is_unix(), 'not unix')
  def test_multi_line_os_linesep_unix(self):
    t = self.call_lex_all(_test_lexer, '''\nfruit=kiwi\ncolor=green\n''',
      [
        ( 't_line_break', os.linesep, ( 1, 1 ), 'h_line_break', None ),
        ( 't_key', 'fruit', ( 2, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 2, 6 ), None, None ),
        ( 't_value', 'kiwi', ( 2, 7 ), None, None ),
        ( 't_line_break', os.linesep, (  2, 11 ), 'h_line_break', None ),
        ( 't_key', 'color', ( 3, 1 ), None, None ),
        ( 't_key_value_delimiter', '=', ( 3, 6 ), None, None ),
        ( 't_value', 'green', ( 3, 7 ), None, None ),
        ( 't_line_break', os.linesep, (  3, 12 ), 'h_line_break', None ),
        ( 't_done', None, None, 'h_done', None ),
      ])
    self.assertMultiLineEqual( t.expected, t.actual )
    self.assertMultiLineEqual( t.expected_source_string, t.actual_source_string )

  def test_lex_all_multiple_times(self):
    l = _test_lexer()
    expected_tokens = btl_lexer_token_list([
      ( 't_key', 'a', ( 1, 1 ), None, None ),
      ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
      ( 't_value', 'k', ( 1, 3 ), None, None ),
      ( 't_done', None, None, 'h_done', None ),
    ])
    expected = '\n'.join([ token.to_debug_str() for token in expected_tokens ])
    actual_tokens = l.lex_all('a=k')
    actual = '\n'.join([ token.to_debug_str() for token in actual_tokens ])
    self.assertEqual( expected, actual )

    expected_tokens = btl_lexer_token_list([
      ( 't_key', 'b', ( 1, 1 ), None, None ),
      ( 't_key_value_delimiter', '=', ( 1, 2 ), None, None ),
      ( 't_value', 'z', ( 1, 3 ), None, None ),
      ( 't_done', None, None, 'h_done', None ),
    ])
    expected = '\n'.join([ token.to_debug_str() for token in expected_tokens ])
    actual_tokens = l.lex_all('b=z')
    actual = '\n'.join([ token.to_debug_str() for token in actual_tokens ])
    self.assertEqual( expected, actual )
    
if __name__ == '__main__':
  unit_test.main()
