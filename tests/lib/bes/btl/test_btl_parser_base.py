#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.system.host import host
from bes.system.check import check
from bes.testing.unit_test import unit_test
from bes.testing.unit_test_function_skip import unit_test_function_skip

from bes.btl.btl_parser_base import btl_parser_base
from bes.btl.btl_parser_state_base import btl_parser_state_base
from bes.btl.btl_parser_tester_mixin import btl_parser_tester_mixin
from bes.btl.btl_parser_runtime_error import btl_parser_runtime_error

from _test_simple_lexer import _test_simple_lexer

class _test_parser(btl_parser_base):

  class e_unexpected_token(btl_parser_runtime_error):
    def __init__(self, message = None):
      super().__init__(message = message)
  
  class _state_s_start(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_start'
      super().__init__(parser, name, log_tag)
      self._first_time = True
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)

      if self._first_time:
        self._first_time = False
        self.node_creator.create_root()
      
      new_state_name = None
  
      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_line_break':
        new_state_name = 's_start'
      elif token.name == 't_space':
        new_state_name = 's_start'
      elif token.name == 't_key':
        new_state_name = 's_expecting_delimiter'
        self.node_creator.create('n_key_value')
        self.node_creator.create('n_key')
        self.node_creator.set_token('n_key', token)
        self.node_creator.add_child('n_key_value', 'n_key')
      elif token.name == 't_comment':
        new_state_name = 's_start'
      else:
        new_state_name = 's_done'

      return new_state_name
  
  class _state_s_expecting_delimiter(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_expecting_delimiter'
      super().__init__(parser, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state_name = None
  
      if token.name == 't_key_value_delimiter':
        new_state_name = 's_expecting_value'
      elif token.name == 't_space':
        new_state_name = 's_expecting_delimiter'
      else:
        new_state_name = 's_done'
      
      return new_state_name
  
  class _state_s_expecting_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_expecting_value'
      super().__init__(parser, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state_name = None
  
      if token.name == 't_value':
        new_state_name = 's_after_value'
        self.node_creator.create('n_value')
        self.node_creator.set_token('n_value', token)
        self.node_creator.add_child('n_key_value', 'n_value')
        self.node_creator.add_child('n_root', 'n_key_value')
      elif token.name == 't_space':
        new_state_name = 's_expecting_value'
      else:
        new_state_name = 's_done'
      
      return new_state_name
  
  class _state_s_after_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_after_value'
      super().__init__(parser, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state_name = None
  
      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_space':
        new_state_name = 's_after_value'
      elif token.name == 't_comment':
        new_state_name = 's_after_value'
      elif token.name == 't_line_break':
        new_state_name = 's_start'
      else:
        new_state_name = 's_done'
      
      return new_state_name
  
  class _state_s_done(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_done'
      super().__init__(parser, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state_name = None
      
      return new_state_name

  def __init__(self, lexer):
    check.check_btl_lexer(lexer)
    desc_text = self._DESC_TEXT
    states = {
      's_start': self._state_s_start(self, lexer.log_tag),
      's_expecting_delimiter': self._state_s_expecting_delimiter(self, lexer.log_tag),
      's_expecting_value': self._state_s_expecting_value(self, lexer.log_tag),
      's_after_value': self._state_s_after_value(self, lexer.log_tag),
      's_done': self._state_s_done(self, lexer.log_tag),
    }
    super().__init__(lexer, desc_text, states)
  _DESC_TEXT = """
#BTP
#
# Key Value pair parser
#
parser
  name: p_simple
  description: A simple key value pair parser
  version: 1.0
  start_state: s_start
  end_state: s_done

errors
  e_unexpected_token: In state "{state_name}" unexpected token: "{token}"

#  t_done
#    type_hint: h_done
#  t_key_value_delimiter
#  t_key
#  t_line_break
#    type_hint: h_line_break
#  t_space
#  t_value

states

  s_start
    transitions
      t_done: s_done
      t_line_break: s_start
      t_space: s_start
      t_key: s_expecting_delimiter
        node create n_key_value
        node create n_key
        node set_token n_key
        node add n_key_value n_key
      t_comment: s_start
      default: s_done
        error e_unexpected_token
    one_time_commands
      node create n_root
    commands

  s_expecting_delimiter
    transitions
      t_key_value_delimiter: s_expecting_value
      t_space: s_expecting_delimiter
      default: s_done
        error e_unexpected_token

  s_expecting_value
    transitions
      t_value: s_after_value
        node create n_value
        node set_token n_value
        node add root n_key_value
      t_space: s_expecting_value
      default: s_done
        error e_unexpected_token

  s_after_value
    transitions
      t_done: s_done
      t_space: s_after_value
      t_comment: s_after_value
      t_line_break: s_start
      default: s_done
        error e_unexpected_token

  s_done
"""
  
class test_btl_parser_base(btl_parser_tester_mixin, unit_test):

  def test_foo(self):
    l = _test_simple_lexer()
    p = _test_parser(l)
    text = '''
fruit=apple
color=red
'''
    root = p.run(text)
    print(root)
    
if __name__ == '__main__':
  unit_test.main()
