
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_runtime_error import btl_lexer_runtime_error
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_token import btl_lexer_token

class _test_simple_parser(btl_lexer_base):

  class e_unexpected_token(btl_parser_runtime_error):
    def __init__(self, message = None):
      super().__init__(message = message)

  
  class _state_s_start(btl_parser_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_start'
      super().__init__(lexer, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state = None
  
      if self.char_in(c, 't_done'):
        new_state = 's_done'
      elif self.char_in(c, 't_line_break'):
        new_state = 's_start'
      elif self.char_in(c, 't_space'):
        new_state = 's_start'
      elif self.char_in(c, 't_key'):
        new_state = 's_expecting_delimiter'
      elif self.char_in(c, 't_comment'):
        new_state = 's_start'
      else:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, token)
      return tokens
  
  class _state_s_expecting_delimiter(btl_parser_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_delimiter'
      super().__init__(lexer, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state = None
  
      if self.char_in(c, 't_key_value_delimiter'):
        new_state = 's_expecting_value'
      elif self.char_in(c, 't_space'):
        new_state = 's_expecting_delimiter'
      else:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, token)
      return tokens
  
  class _state_s_expecting_value(btl_parser_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state = None
  
      if self.char_in(c, 't_value'):
        new_state = 's_after_value'
      elif self.char_in(c, 't_space'):
        new_state = 's_expecting_value'
      else:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, token)
      return tokens
  
  class _state_s_after_value(btl_parser_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_after_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state = None
  
      if self.char_in(c, 't_done'):
        new_state = 's_done'
      elif self.char_in(c, 't_space'):
        new_state = 's_after_value'
      elif self.char_in(c, 't_comment'):
        new_state = 's_after_value'
      elif self.char_in(c, 't_line_break'):
        new_state = 's_start'
      else:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, token)
      return tokens
  
  class _state_s_done(btl_parser_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_done'
      super().__init__(lexer, name, log_tag)
  
    def handle_token(self, token):
      token = check.check_btl_lexer_token(token)
      self.log_handle_token(token)
  
      new_state = None
  
      
      self.lexer.change_state(new_state, token)
      return tokens

  def __init__(self, source = None):
    log_tag = f'_test_simple_parser'
    desc_text = self._DESC_TEXT
    token = self._token
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_expecting_delimiter': self._state_s_expecting_delimiter(self, log_tag),
      's_expecting_value': self._state_s_expecting_value(self, log_tag),
      's_after_value': self._state_s_after_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, desc_text, token, states, source = source)
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
check.register_class(_test_simple_parser, include_seq = False)
