
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_runtime_error import btl_lexer_runtime_error
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_token import btl_lexer_token

class _test_keyval1_lexer(btl_lexer_base):

  class _token:

    T_DONE = 't_done'
    T_KEY = 't_key'
    T_KEY_VALUE_DELIMITER = 't_key_value_delimiter'
    T_LINE_BREAK = 't_line_break'
    T_SPACE = 't_space'
    T_VALUE = 't_value'

  class e_unexpected_char(btl_lexer_runtime_error):
    def __init__(self, message = None):
      super().__init__(message = message)

  
  class _state_s_start(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_start'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', args = {}))
      elif self.char_in(c, 'c_nl'):
        new_state = 's_start'
        self.buffer_write(c)
        tokens.append(self.make_token('t_line_break', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_ws'):
        new_state = 's_start'
        tokens.append(self.make_token('t_space', args = {}))
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state = 's_key'
        self.buffer_write(c)
      else:
        new_state = 's_done'
        name = self.name
        char = c
        msg = f'In state {state} unexpected character {char} instead of key'
        raise self.lexer.e_unexpected_char(message = msg)
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_key(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_key'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_keyval_key'):
        new_state = 's_key'
        self.buffer_write(c)
      elif self.char_in(c, 'c_equal'):
        new_state = 's_value'
        tokens.append(self.make_token('t_key', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
        tokens.append(self.make_token('t_key_value_delimiter', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_key', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_done', args = {}))
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_value(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_nl'):
        new_state = 's_start'
        tokens.append(self.make_token('t_value', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
        tokens.append(self.make_token('t_line_break', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_value', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_done', args = {}))
      else:
        new_state = 's_value'
        self.buffer_write(c)
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_done(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_done'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      
      self.lexer.change_state(new_state, c)
      return tokens

  def __init__(self, source = None):
    log_tag = f'_test_keyval1_lexer'
    desc_text = self._DESC_TEXT
    token = self._token
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_key': self._state_s_key(self, log_tag),
      's_value': self._state_s_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, desc_text, token, states, source = source)
  _DESC_TEXT = """
#BTL
#
# Key Value pair lexer
#
lexer
  name: keyval
  description: A Key Value pair lexer
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
  e_unexpected_char: In state {state} unexpected character {char} instead of key

chars
  c_keyval_key_first: c_underscore | c_alpha
  c_keyval_key: c_keyval_key_first | c_numeric

states

  s_start
    c_eos: s_done
      emit t_done
    c_nl: s_start
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
    c_equal: s_value
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
    c_nl: s_start
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
check.register_class(_test_keyval1_lexer, include_seq = False)
