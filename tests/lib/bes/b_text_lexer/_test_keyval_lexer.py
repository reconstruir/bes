
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
  
      if self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', self.buffer_value(), self.position))
      elif self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_line_break', self.buffer_value(), self.position))
      elif self.char_in(c, 'c_ws'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_space', self.buffer_value(), self.position))
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state = 's_key'
        self.buffer_write(c)
      else:
        new_state = 's_expecting_key_error'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _test_keyval_lexer_state_s_expecting_key_error(btl_lexer_state_base):
    def __init__(self, lexer):
      super().__init__(lexer)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if True:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _test_keyval_lexer_state_s_key(btl_lexer_state_base):
    def __init__(self, lexer):
      super().__init__(lexer)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_keyval_key'):
        new_state = 's_key'
        self.buffer_write(c)
      elif self.char_in(c, 'c_equal'):
        new_state = 's_value'
        tokens.append(self.make_token('t_key', self.buffer_value(), self.position))
        self.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', self.buffer_value(), self.position))
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _test_keyval_lexer_state_s_value(btl_lexer_state_base):
    def __init__(self, lexer):
      super().__init__(lexer)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_value', self.buffer_value(), self.position))
        self.buffer_reset()
        tokens.append(self.make_token('t_line_break', self.buffer_value(), self.position))
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', self.buffer_value(), self.position))
      else:
        new_state = 's_value'
        self.buffer_write(c)
      
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
      's_expecting_key_error': self._test_keyval_lexer_state_s_expecting_key_error(self),
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
  s_expecting_key_error
    default: s_done
  s_key
    c_keyval_key: s_key
      buffer write
    c_equal: s_value
      yield t_key
      buffer reset
    c_eos: s_done
      yield t_done
  s_value
    c_nl: s_expecting_key
      yield t_value
      buffer reset
      yield t_line_break
    c_eos: s_done
      yield t_done
    default: s_value
      buffer write
  s_done

"""
check.register_class(_test_keyval_lexer, include_seq = False)
