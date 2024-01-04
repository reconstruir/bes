
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_lexer_base import btl_lexer_base
from bes.b_text_lexer.btl_lexer_state_base import btl_lexer_state_base
from bes.b_text_lexer.btl_lexer_token import btl_lexer_token
from bes.system.check import check

class _test_keyval2_lexer(btl_lexer_base):

  class _token:

    T_DONE = 't_done'
    T_EQUAL = 't_equal'
    T_KEY = 't_key'
    T_LINE_BREAK = 't_line_break'
    T_SPACE = 't_space'
    T_VALUE = 't_value'
  
  class _state_s_expecting_key(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_key'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', args = {}))
      elif self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_line_break', args = {}))
      elif self.char_in(c, 'c_ws'):
        new_state = 's_before_key_space'
        self.buffer_write(c)
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state = 's_key'
        self.buffer_write(c)
      else:
        new_state = 's_expecting_key_error'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_before_key_space(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_before_key_space'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_ws'):
        new_state = 's_before_key_space'
        self.buffer_write(c)
      elif self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_space', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_line_break', args = {}))
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state = 's_key'
        tokens.append(self.make_token('t_space', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
      else:
        new_state = 's_expecting_key_error'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_after_key_space(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_after_key_space'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_ws'):
        new_state = 's_after_key_space'
        self.buffer_write(c)
      elif self.char_in(c, 'c_equal'):
        new_state = 's_expecting_value'
        tokens.append(self.make_token('t_space', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
        tokens.append(self.make_token('t_equal', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', args = {}))
      else:
        new_state = 's_expecting_equal_error'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_before_value_space(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_before_value_space'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_ws'):
        new_state = 's_value_key_space'
        self.buffer_write(c)
      elif self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_space', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_line_break', args = {}))
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state = 's_value'
        tokens.append(self.make_token('t_space', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_space', args = {}))
        tokens.append(self.make_token('t_done', args = {}))
      else:
        new_state = 's_expecting_value_error'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_expecting_value(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if self.char_in(c, 'c_ws'):
        new_state = 's_before_value_space'
        self.buffer_write(c)
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_done', args = {}))
      elif self.char_in(c, 'c_nl'):
        new_state = 's_expecting_key'
        self.buffer_reset()
        tokens.append(self.make_token('t_line_break', args = {}))
      elif self.char_in(c, 'c_keyval_key_first'):
        new_state = 's_value'
        self.buffer_write(c)
      else:
        new_state = 's_value'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_expecting_key_error(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_key_error'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if True:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_expecting_equal_error(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_equal_error'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if True:
        new_state = 's_done'
      
      self.lexer.change_state(new_state, c)
      return tokens
  
  class _state_s_expecting_value_error(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_value_error'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, c):
      self.log_handle_char(c)
  
      new_state = None
      tokens = []
  
      if True:
        new_state = 's_done'
      
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
        new_state = 's_expecting_value'
        tokens.append(self.make_token('t_key', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
        tokens.append(self.make_token('t_equal', args = {}))
        self.buffer_reset()
      elif self.char_in(c, 'c_eos'):
        new_state = 's_done'
        tokens.append(self.make_token('t_key', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_done', args = {}))
      elif self.char_in(c, 'c_ws'):
        new_state = 's_after_key_space'
        tokens.append(self.make_token('t_key', args = {}))
        self.buffer_reset()
        self.buffer_write(c)
      
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
        new_state = 's_expecting_key'
        tokens.append(self.make_token('t_value', args = {}))
        self.buffer_reset()
        tokens.append(self.make_token('t_line_break', args = {}))
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
    log_tag = f'_test_keyval2_lexer'
    desc_text = self._DESC_TEXT
    token = self._token
    states = {
      's_expecting_key': self._state_s_expecting_key(self, log_tag),
      's_before_key_space': self._state_s_before_key_space(self, log_tag),
      's_after_key_space': self._state_s_after_key_space(self, log_tag),
      's_before_value_space': self._state_s_before_value_space(self, log_tag),
      's_expecting_value': self._state_s_expecting_value(self, log_tag),
      's_expecting_key_error': self._state_s_expecting_key_error(self, log_tag),
      's_expecting_equal_error': self._state_s_expecting_equal_error(self, log_tag),
      's_expecting_value_error': self._state_s_expecting_value_error(self, log_tag),
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
  version: 2.0
  start_state: s_expecting_key
  end_state: s_done

tokens
  t_done
    type_hint: done
  t_equal
  t_key
  t_line_break
    type_hint: line_break
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
    c_ws: s_before_key_space
      buffer write
    c_keyval_key_first: s_key
      buffer write
    default: s_expecting_key_error
      raise unexpected_char

  s_before_key_space
    c_ws: s_before_key_space
      buffer write
    c_nl: s_expecting_key
      yield t_space
      buffer reset
      yield t_line_break
    c_keyval_key_first: s_key
      yield t_space
      buffer reset
      buffer write
    default: s_expecting_key_error
      raise unexpected_char

  s_after_key_space
    c_ws: s_after_key_space
      buffer write
    c_equal: s_expecting_value
      yield t_space
      buffer reset
      buffer write
      yield t_equal
      buffer reset
    c_eos: s_done
      yield t_done
    default: s_expecting_equal_error
      raise unexpected_char

  s_before_value_space
    c_ws: s_value_key_space
      buffer write
    c_nl: s_expecting_key
      yield t_space
      buffer reset
      yield t_line_break
    c_keyval_key_first: s_value
      yield t_space
      buffer reset
      buffer write
    c_eos: s_done
      yield t_space
      yield t_done
    default: s_expecting_value_error
      raise unexpected_char

  s_expecting_value
    c_ws: s_before_value_space
      buffer write
    c_eos: s_done
      yield t_done
    c_nl: s_expecting_key
      buffer reset
      yield t_line_break
    c_keyval_key_first: s_value
      buffer write
    default: s_value
      raise unexpected_char

  s_expecting_key_error
    default: s_done

  s_expecting_equal_error
    default: s_done

  s_expecting_value_error
    default: s_done

  s_key
    c_keyval_key: s_key
      buffer write
    c_equal: s_expecting_value
      yield t_key
      buffer reset
      buffer write
      yield t_equal
      buffer reset
    c_eos: s_done
      yield t_key
      buffer reset
      yield t_done
    c_ws: s_after_key_space
      yield t_key
      buffer reset
      buffer write
      
  s_value
    c_nl: s_expecting_key
      yield t_value
      buffer reset
      yield t_line_break
    c_eos: s_done
      yield t_value
      buffer reset
      yield t_done
    default: s_value
      buffer write
      
  s_done

"""
check.register_class(_test_keyval2_lexer, include_seq = False)
