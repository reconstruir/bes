#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from bes.system.host import host
from bes.system.check import check
from bes.testing.unit_test import unit_test

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

    def enter_state(self, context):
      self.log_d(f'{self.name}: enter_state')

    def leave_state(self, context):
      self.log_d(f'{self.name}: leave_state')
      
    def handle_token(self, context, token):
      self.log_handle_token(token)

#      if first_time:
#        context.node_creator.create_root()
      
      new_state_name = None
  
      if token.name == 't_done':
        new_state_name = 's_done'
      elif token.name == 't_line_break':
        new_state_name = 's_start'
      elif token.name == 't_space':
        new_state_name = 's_start'
      elif token.name == 't_key':
        new_state_name = 's_expecting_delimiter'
        context.node_creator.create('n_key_value')
        context.node_creator.create('n_key')
        context.node_creator.set_token('n_key', token)
        context.node_creator.add_child('n_key_value', 'n_key')
      elif token.name == 't_comment':
        new_state_name = 's_start'
      else:
        new_state_name = 's_done'

      return new_state_name
  
  class _state_s_expecting_delimiter(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_expecting_delimiter'
      super().__init__(parser, name, log_tag)

    def enter_state(self, context):
      self.log_d(f'{self.name}: enter_state')

    def leave_state(self, context):
      self.log_d(f'{self.name}: leave_state')
      
    def handle_token(self, context, token):
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

    def enter_state(self, context):
      self.log_d(f'{self.name}: enter_state')

    def leave_state(self, context):
      self.log_d(f'{self.name}: leave_state')
      
    def handle_token(self, context, token):
      self.log_handle_token(token)
  
      new_state_name = None
  
      if token.name == 't_value':
        new_state_name = 's_after_value'
        context.node_creator.create('n_value')
        context.node_creator.set_token('n_value', token)
        context.node_creator.add_child('n_key_value', 'n_value')
        context.node_creator.add_child('n_root', 'n_key_value')
      elif token.name == 't_space':
        new_state_name = 's_expecting_value'
      else:
        new_state_name = 's_done'
      
      return new_state_name
  
  class _state_s_after_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_after_value'
      super().__init__(parser, name, log_tag)

    def enter_state(self, context):
      self.log_d(f'{self.name}: enter_state')

    def leave_state(self, context):
      self.log_d(f'{self.name}: leave_state')
      
    def handle_token(self, context, token):
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

    def enter_state(self, context):
      self.log_d(f'{self.name}: enter_state')

    def leave_state(self, context):
      self.log_d(f'{self.name}: leave_state')
      
    def handle_token(self, context, token):
      self.log_handle_token(token)
  
      new_state_name = None
      
      return new_state_name

  def __init__(self, lexer):
    check.check_btl_lexer(lexer)
    log_tag = '_test_parser'
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_expecting_delimiter': self._state_s_expecting_delimiter(self, log_tag),
      's_expecting_value': self._state_s_expecting_value(self, log_tag),
      's_after_value': self._state_s_after_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, lexer, states)

  def do_start_commands(self, context):
    self.log_d(f'do_start_commands:')
    context.node_creator.create_root()
  
  def do_end_commands(self, context):
    self.log_d(f'do_start_commands:')

  @classmethod
  #@abstractmethod
  def desc_source(clazz):
    return 'test_btl_parser_base.py'
    
  @classmethod
  #@abstractmethod
  def desc_text(clazz):
    return """\
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
  e_unexpected_token: In state "{self.name}" unexpected token: "{token.name}"

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

  def test_parse(self):
    l = _test_simple_lexer()
    p = _test_parser(l)
    text = '''
fruit=apple
color=red

fruit=kiwi
color=green
'''
    result = p.parse(text)
    self.assert_python_code_text_equal( '''
n_root;
  n_key_value;
    n_key;t_key:fruit:p=2,1:i=1
    n_value;t_value:apple:p=2,7:i=3
  n_key_value;
    n_key;t_key:color:p=3,1:i=5
    n_value;t_value:red:p=3,7:i=7
  n_key_value;
    n_key;t_key:fruit:p=5,1:i=10
    n_value;t_value:kiwi:p=5,7:i=12
  n_key_value;
    n_key;t_key:color:p=6,1:i=14
    n_value;t_value:green:p=6,7:i=16
''', str(result.root_node) )

    self.assert_multi_line_xp_equal('''\
 0: t_line_break:[NL]:p=1,1:h=h_line_break:i=0
 1: t_key:fruit:p=2,1:i=1
 2: t_key_value_delimiter:=:p=2,6:i=2
 3: t_value:apple:p=2,7:i=3
 4: t_line_break:[NL]:p=2,12:h=h_line_break:i=4
 5: t_key:color:p=3,1:i=5
 6: t_key_value_delimiter:=:p=3,6:i=6
 7: t_value:red:p=3,7:i=7
 8: t_line_break:[NL]:p=3,10:h=h_line_break:i=8
 9: t_line_break:[NL]:p=4,1:h=h_line_break:i=9
10: t_key:fruit:p=5,1:i=10
11: t_key_value_delimiter:=:p=5,6:i=11
12: t_value:kiwi:p=5,7:i=12
13: t_line_break:[NL]:p=5,11:h=h_line_break:i=13
14: t_key:color:p=6,1:i=14
15: t_key_value_delimiter:=:p=6,6:i=15
16: t_value:green:p=6,7:i=16
17: t_line_break:[NL]:p=6,12:h=h_line_break:i=17
18: t_done::h=h_done:i=18
''', result.tokens.to_debug_str() )

    tree_token_ids = set()
    def _visitor(node):
      if node.token:
        tree_token_ids.add(id(node.token))
    result.root_node.visit_children(_visitor, recurse = True)
    list_token_ids = set([ id(token) for token in result.tokens ])
    for token_id in tree_token_ids:
      self.assertEqual( True, token_id in list_token_ids )
      
if __name__ == '__main__':
  unit_test.main()
