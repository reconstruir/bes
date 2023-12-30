
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_lexer_base import btl_lexer_base
from bes.b_text_lexer.btl_lexer_state_base import btl_lexer_state_base
from bes.b_text_lexer.btl_lexer_token import btl_lexer_token
from bes.system.check import check


class _test_keyval_lexer(btl_lexer_base):
  
  class _test_keyval_lexer_token(object):
    def __init__(self, lexer):
      check.check__test_keyval_lexer(lexer)
    
      self._lexer = lexer
    
    T_DONE = 't_done'
    def make_t_done(self, value):
      return btl_lexer_token(self.T_DONE, value, self._lexer.position)
    
    T_EXPECTING_KEY = 't_expecting_key'
    def make_t_expecting_key(self, value):
      return btl_lexer_token(self.T_EXPECTING_KEY, value, self._lexer.position)
    
    T_KEY = 't_key'
    def make_t_key(self, value):
      return btl_lexer_token(self.T_KEY, value, self._lexer.position)
    
    T_LINE_BREAK = 't_line_break'
    def make_t_line_break(self, value):
      return btl_lexer_token(self.T_LINE_BREAK, value, self._lexer.position)
    
    T_SPACE = 't_space'
    def make_t_space(self, value):
      return btl_lexer_token(self.T_SPACE, value, self._lexer.position)
    
    T_VALUE = 't_value'
    def make_t_value(self, value):
      return btl_lexer_token(self.T_VALUE, value, self._lexer.position)
  
  class _test_keyval_lexer_state_s_expecting_key(btl_lexer_state_base):
    def __init__(self, lexer):
      super().__init__(lexer)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if c in {0}:
        new_state = s_done
        tokens.append(self.make_token(t_done, self.buffer_value(), self.position))
      elif c in {10}:
        new_state = s_expecting_key
        tokens.append(self.make_token(t_line_break, self.buffer_value(), self.position))
      elif c in {32, 9}:
        new_state = s_expecting_key
        tokens.append(self.make_token(t_space, self.buffer_value(), self.position))
      elif c in {65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122}:
        new_state = s_key
        self.lexer.buffer_write(c)
      else:
        new_state = s_expecting_key_error
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _test_keyval_lexer_state_s_key(btl_lexer_state_base):
    def __init__(self, lexer):
      super().__init__(lexer)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if c in {48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 95, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122}:
        new_state = s_key
        self.lexer.buffer_write(c)
      elif c in {61}:
        new_state = s_value
        tokens.append(self.make_token(t_key, self.buffer_value(), self.position))
      elif c in {0}:
        new_state = s_done
        tokens.append(self.make_token(t_done, self.buffer_value(), self.position))
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _test_keyval_lexer_state_s_value(btl_lexer_state_base):
    def __init__(self, lexer):
      super().__init__(lexer)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if c in {10}:
        new_state = s_expecting_key
        tokens.append(self.make_token(t_line_break, self.buffer_value(), self.position))
        tokens.append(self.make_token(t_value, self.buffer_value(), self.position))
      elif c in {0}:
        new_state = s_done
        tokens.append(self.make_token(t_done, self.buffer_value(), self.position))
      else:
        new_state = s_value
        self.lexer.buffer_write(c)
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _test_keyval_lexer_state_s_done(btl_lexer_state_base):
    def __init__(self, lexer):
      super().__init__(lexer)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      
      self.lexer.change_state(new_state, c)
      return tokens

  def __init__(self, source = None):
    log_tag = f'_test_keyval'
    desc_text = self._DESC_TEXT
    token = self._test_keyval_lexer_token(self)
    states = {
      's_expecting_key': self._test_keyval_lexer_state_s_expecting_key(self),
      's_key': self._test_keyval_lexer_state_s_key(self),
      's_value': self._test_keyval_lexer_state_s_value(self),
      's_done': self._test_keyval_lexer_state_s_done(self),
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
  start_state: s_expecting_key
  end_state: s_done

tokens
  t_done
  t_key
  t_expecting_key
  t_line_break
  t_space
  t_value

errors
  unexpected_char: In state {state} unexpected character {char} instead of key

chars
  c_keyval_key_first: c_underscore | c_alpha
  c_keyval_key: c_keyval_key_first | c_numeric

states
  s_expecting_key
    c_eos: s_done
      yield t_done
    c_nl: s_expecting_key
      yield t_line_break
    c_ws: s_expecting_key
      yield t_space 
    c_keyval_key_first: s_key
      buffer write
    default: s_expecting_key_error
      raise unexpected_char
  s_key
    c_keyval_key: s_key
      buffer write
    c_equal: s_value
      yield t_key
    c_eos: s_done
      yield t_done
  s_value
    c_nl: s_expecting_key
      yield t_line_break
      yield t_value
    c_eos: s_done
      yield t_done
    default: s_value
      buffer write
  s_done

"""
check.register_class(_test_keyval_lexer, include_seq = False)
