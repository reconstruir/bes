
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_function_base import btl_function_base
from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_runtime_error import btl_lexer_runtime_error
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_token import btl_lexer_token

class bc_ini_lexer(btl_lexer_base):

  class _token:

    T_COMMENT = 't_comment'
    T_COMMENT_BEGIN = 't_comment_begin'
    T_DONE = 't_done'
    T_KEY = 't_key'
    T_KEY_VALUE_DELIMITER = 't_key_value_delimiter'
    T_LINE_BREAK = 't_line_break'
    T_SECTION_NAME = 't_section_name'
    T_SECTION_NAME_BEGIN = 't_section_name_begin'
    T_SECTION_NAME_END = 't_section_name_end'
    T_SPACE = 't_space'
    T_VALUE = 't_value'

  class e_unexpected_char(btl_lexer_runtime_error):
    pass
  class e_unexpected_eos(btl_lexer_runtime_error):
    pass

  
  class _function_f_handle_comment_begin(btl_function_base):
    def call(self, context, tokens, c, current_token_name):
      tokens.append(self.make_token(context, current_token_name))
      context.buffer_reset()
      context.buffer_write(c)
      tokens.append(self.make_token(context, 't_comment_begin'))
      context.buffer_reset()

  
  class _state_s_start(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_start'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_keyval_key_first', context):
        new_state_name = 's_key'
        context.buffer_write(c)
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_done'))
      elif self.char_in(c, 'c_comment_begin', context):
        new_state_name = 's_comment'
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_comment_begin'))
        context.buffer_reset()
      elif self.char_in(c, 'c_ws', context):
        new_state_name = 's_before_key_space'
        context.buffer_write(c)
      elif self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
        context.buffer_reset()
      elif self.char_in(c, 'c_open_bracket', context):
        new_state_name = 's_section_name'
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_section_name_begin'))
        context.buffer_reset()
      else:
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_comment(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_comment'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_comment'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_comment'))
        context.buffer_reset()
        tokens.append(self.make_token(context, 't_done'))
      else:
        new_state_name = 's_comment'
        context.buffer_write(c)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_section_name(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_section_name'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_section_name', context):
        new_state_name = 's_section_name'
        context.buffer_write(c)
      elif self.char_in(c, 'c_close_bracket', context):
        new_state_name = 's_after_section_name'
        tokens.append(self.make_token(context, 't_section_name'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_section_name_end'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      else:
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_after_section_name(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_after_section_name'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_ws', context):
        new_state_name = 's_after_section_name_space'
        context.buffer_write(c)
      elif self.char_in(c, 'c_comment_begin', context):
        new_state_name = 's_comment'
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_comment_begin'))
        context.buffer_reset()
      elif self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_done'))
      else:
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_after_section_name_space(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_after_section_name_space'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_ws', context):
        new_state_name = 's_after_section_name_space'
        context.buffer_write(c)
      elif self.char_in(c, 'c_comment_begin', context):
        new_state_name = 's_comment'
        self.lexer._function_f_handle_comment_begin(self).call(context, tokens, c, 't_space')
      elif self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_space'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_done'))
      else:
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_before_key_space(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_before_key_space'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_ws', context):
        new_state_name = 's_before_key_space'
        context.buffer_write(c)
      elif self.char_in(c, 'c_comment_begin', context):
        new_state_name = 's_comment'
        self.lexer._function_f_handle_comment_begin(self).call(context, tokens, c, 't_space')
      elif self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_space'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
        context.buffer_reset()
      elif self.char_in(c, 'c_keyval_key_first', context):
        new_state_name = 's_key'
        tokens.append(self.make_token(context, 't_space'))
        context.buffer_reset()
        context.buffer_write(c)
      else:
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_after_key_space(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_after_key_space'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_ws', context):
        new_state_name = 's_after_key_space'
        context.buffer_write(c)
      elif self.char_in(c, 'c_key_value_delimiter', context):
        new_state_name = 's_expecting_value'
        tokens.append(self.make_token(context, 't_space'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_key_value_delimiter'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_done'))
      else:
        new_state_name = 's_done'
        message = f'In state "{self.name}" unexpected character: "{c}"'
        raise self.lexer.e_unexpected_char(context, message)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_before_value_space(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_before_value_space'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_ws', context):
        new_state_name = 's_before_value_space'
        context.buffer_write(c)
      elif self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        tokens.append(self.make_token(context, 't_space'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_space'))
        tokens.append(self.make_token(context, 't_done'))
      elif self.char_in(c, 'c_comment_begin', context):
        new_state_name = 's_comment'
        self.lexer._function_f_handle_comment_begin(self).call(context, tokens, c, 't_space')
      else:
        new_state_name = 's_value'
        tokens.append(self.make_token(context, 't_space'))
        context.buffer_reset()
        context.buffer_write(c)
      
      return self._handle_char_result(new_state_name, tokens)
  
  class _state_s_expecting_value(btl_lexer_state_base):
    def __init__(self, lexer, log_tag):
      name = 's_expecting_value'
      super().__init__(lexer, name, log_tag)
  
    def handle_char(self, context, c):
      self.log_handle_char(context, c)
  
      new_state_name = None
      tokens = []
  
      if self.char_in(c, 'c_ws', context):
        new_state_name = 's_before_value_space'
        context.buffer_write(c)
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_done'))
      elif self.char_in(c, 'c_line_break', context):
        new_state_name = 's_start'
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_line_break'))
      else:
        new_state_name = 's_value'
        context.buffer_write(c)
      
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
        new_state_name = 's_expecting_value'
        tokens.append(self.make_token(context, 't_key'))
        context.buffer_reset()
        context.buffer_write(c)
        tokens.append(self.make_token(context, 't_key_value_delimiter'))
        context.buffer_reset()
      elif self.char_in(c, 'c_eos', context):
        new_state_name = 's_done'
        tokens.append(self.make_token(context, 't_key'))
        context.buffer_reset()
        tokens.append(self.make_token(context, 't_done'))
      elif self.char_in(c, 'c_ws', context):
        new_state_name = 's_after_key_space'
        tokens.append(self.make_token(context, 't_key'))
        context.buffer_reset()
        context.buffer_write(c)
      
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
        tokens.append(self.make_token(context, 't_value'))
        context.buffer_reset()
        tokens.append(self.make_token(context, 't_done'))
      elif self.char_in(c, 'c_comment_begin', context):
        new_state_name = 's_comment'
        self.lexer._function_f_handle_comment_begin(self).call(context, tokens, c, 't_value')
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
    log_tag = f'bc_ini_lexer'
    desc_text = self._DESC_TEXT
    token = self._token
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_comment': self._state_s_comment(self, log_tag),
      's_section_name': self._state_s_section_name(self, log_tag),
      's_after_section_name': self._state_s_after_section_name(self, log_tag),
      's_after_section_name_space': self._state_s_after_section_name_space(self, log_tag),
      's_before_key_space': self._state_s_before_key_space(self, log_tag),
      's_after_key_space': self._state_s_after_key_space(self, log_tag),
      's_before_value_space': self._state_s_before_value_space(self, log_tag),
      's_expecting_value': self._state_s_expecting_value(self, log_tag),
      's_key': self._state_s_key(self, log_tag),
      's_value': self._state_s_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, desc_text, token, states, desc_source = desc_source)
  _DESC_TEXT = """
#BTL
#
lexer
  name: bc_ini_lexer
  description: A ini style config file lexer
  version: 1.0
  start_state: s_start
  end_state: s_done

tokens
  t_comment
  t_done
    type_hint: h_done
  t_key_value_delimiter
  t_comment_begin
  t_key
  t_line_break
    type_hint: h_line_break
  t_section_name
  t_section_name_begin
  t_section_name_end
  t_space
  t_value

errors
  e_unexpected_char: In state "{self.name}" unexpected character: "{c}"
  e_unexpected_eos: In state "{self.name}" unexpected end-of-string

variables
  v_comment_begin: ;
  v_key_value_delimiter: =

chars
  c_keyval_key_first: c_underscore | c_alpha | c_numeric | c_period
  c_keyval_key: c_keyval_key_first # | c_numeric
  c_section_name: c_underscore | c_alpha | c_numeric | c_period
  c_comment_begin: ${v_comment_begin}
  c_key_value_delimiter: c_equal
  
functions

  f_handle_comment_begin(current_token_name)
    emit ${current_token_name}
    buffer reset
    buffer write
    emit t_comment_begin
    buffer reset

states

  s_start
    c_keyval_key_first: s_key
      buffer write
    c_eos: s_done
      emit t_done
    c_comment_begin: s_comment
      buffer write
      emit t_comment_begin
      buffer reset
    c_ws: s_before_key_space
      buffer write
    c_line_break: s_start
      buffer write
      emit t_line_break
      buffer reset
    c_open_bracket: s_section_name
      buffer write
      emit t_section_name_begin
      buffer reset
    default: s_done
      error e_unexpected_char

  s_comment
    c_line_break: s_start
      emit t_comment
      buffer reset
      buffer write
      emit t_line_break
      buffer reset
    c_eos: s_done
      emit t_comment
      buffer reset 
      emit t_done
    default: s_comment
      buffer write

  s_section_name
    c_section_name: s_section_name
      buffer write
    c_close_bracket: s_after_section_name
      emit t_section_name
      buffer reset
      buffer write
      emit t_section_name_end
      buffer reset
    c_eos: s_done
      error e_unexpected_char
    default: s_done
      error e_unexpected_char

  s_after_section_name
    c_ws: s_after_section_name_space
      buffer write
    c_comment_begin: s_comment
      buffer write
      emit t_comment_begin
      buffer reset
    c_line_break: s_start
      buffer reset
      buffer write
      emit t_line_break
      buffer reset
    c_eos: s_done
      emit t_done
    default: s_done
      error e_unexpected_char

  s_after_section_name_space
    c_ws: s_after_section_name_space
      buffer write
    c_comment_begin: s_comment
      function f_handle_comment_begin 't_space'
    c_line_break: s_start
      emit t_space
      buffer reset
      buffer write
      emit t_line_break
      buffer reset
    c_eos: s_done
      emit t_done
    default: s_done
      error e_unexpected_char

  s_before_key_space
    c_ws: s_before_key_space
      buffer write
    c_comment_begin: s_comment
      function f_handle_comment_begin 't_space'
    c_line_break: s_start
      emit t_space
      buffer reset
      buffer write
      emit t_line_break
      buffer reset
    c_keyval_key_first: s_key
      emit t_space
      buffer reset
      buffer write
    default: s_done
      error e_unexpected_char

  s_after_key_space
    c_ws: s_after_key_space
      buffer write
    c_key_value_delimiter: s_expecting_value
      emit t_space
      buffer reset
      buffer write
      emit t_key_value_delimiter
      buffer reset
    c_eos: s_done
      emit t_done
    default: s_done
      error e_unexpected_char

  s_before_value_space
    c_ws: s_before_value_space
      buffer write
    c_line_break: s_start
      emit t_space
      buffer reset
      buffer write
      emit t_line_break
    c_eos: s_done
      emit t_space
      emit t_done
    c_comment_begin: s_comment
      function f_handle_comment_begin 't_space'
    default: s_value
      emit t_space
      buffer reset
      buffer write

  s_expecting_value
    c_ws: s_before_value_space
      buffer write
    c_eos: s_done
      emit t_done
    c_line_break: s_start
      buffer write
      emit t_line_break
    default: s_value
      buffer write

  s_key
    c_keyval_key: s_key
      buffer write
    c_key_value_delimiter: s_expecting_value
      emit t_key
      buffer reset
      buffer write
      emit t_key_value_delimiter
      buffer reset
    c_eos: s_done
      emit t_key
      buffer reset
      emit t_done
    c_ws: s_after_key_space
      emit t_key
      buffer reset
      buffer write
      
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
    c_comment_begin: s_comment
      function f_handle_comment_begin 't_value'
    default: s_value
      buffer write

  s_done

"""
check.register_class(bc_ini_lexer, include_seq = False)
