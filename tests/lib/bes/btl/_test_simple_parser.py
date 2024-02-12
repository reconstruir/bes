
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_parser_base import btl_parser_base
from bes.btl.btl_parser_runtime_error import btl_parser_runtime_error
from bes.btl.btl_parser_state_base import btl_parser_state_base

class _test_simple_parser(btl_parser_base):

  class e_unexpected_token(btl_parser_runtime_error):
    def __init__(self, message = None):
      super().__init__(message = message)

  
  class _state_s_start(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_start'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_start: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_start: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
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
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_expecting_delimiter(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_expecting_delimiter'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_expecting_delimiter: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_expecting_delimiter: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      if token.name == 't_key_value_delimiter':
        new_state_name = 's_expecting_value'
      elif token.name == 't_space':
        new_state_name = 's_expecting_delimiter'
      else:
        new_state_name = 's_done'
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_expecting_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_expecting_value'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_expecting_value: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_expecting_value: leave_state')
  
    def handle_token(self, context, token, first_time):
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
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_after_value(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_after_value'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_after_value: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_after_value: leave_state')
  
    def handle_token(self, context, token, first_time):
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
        state_name = self.name
        msg = f'In state "{state_name}" unexpected token: "{token}"'
        raise self.lexer.e_unexpected_token(message = msg)
      
      return new_state_name
  
  class _state_s_done(btl_parser_state_base):
    def __init__(self, parser, log_tag):
      name = 's_done'
      super().__init__(parser, name, log_tag)
  
    def enter_state(self, context):
      self.log_d(f's_done: enter_state')
  
    def leave_state(self, context):
      self.log_d(f's_done: leave_state')
  
    def handle_token(self, context, token, first_time):
      self.log_handle_token(token)
      new_state_name = None
      
      return new_state_name

  def __init__(self, lexer):
    check.check_btl_lexer(lexer)
    
    log_tag = f'_test_simple_parser'
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_expecting_delimiter': self._state_s_expecting_delimiter(self, log_tag),
      's_expecting_value': self._state_s_expecting_value(self, log_tag),
      's_after_value': self._state_s_after_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, lexer, self._DESC_TEXT, states)
  
  def do_start_commands(self, context):
    self.log_d(f'do_start_commands:')
    context.node_creator.create_root()
  
  def do_end_commands(self, context):
    self.log_d(f'do_start_commands:')
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
        node add_child n_key_value n_key
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
        node add_child n_key_value n_value
        node add_child n_root n_key_value
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

start_commands
  node create_root n_root

end_commands

"""
check.register_class(_test_simple_parser, include_seq = False)
