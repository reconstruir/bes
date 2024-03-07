
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_function_base import btl_function_base
from bes.btl.btl_lexer_base import btl_lexer_base
from bes.btl.btl_lexer_runtime_error import btl_lexer_runtime_error
from bes.btl.btl_lexer_state_base import btl_lexer_state_base
from bes.btl.btl_lexer_token import btl_lexer_token

class _test_simple_lexer(btl_lexer_base):

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
    def call(self, context, tokens, c, token_name):
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
        self.lexer._function_f_handle_eos(self).call(context, tokens, c, 't_key')

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
        self.lexer._function_f_handle_eos(self).call(context, tokens, c, 't_value')
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

  def __init__(self):
    log_tag = f'_test_simple_lexer'
    token = self._token
    states = {
      's_start': self._state_s_start(self, log_tag),
      's_key': self._state_s_key(self, log_tag),
      's_value': self._state_s_value(self, log_tag),
      's_done': self._state_s_done(self, log_tag),
    }
    super().__init__(log_tag, token, states)

  @classmethod
  #@abstractmethod
  def desc_source(clazz):
    return '_test_simple_lexer.btl'

  @classmethod
  #@abstractmethod
  def desc_text(clazz):
    return """\
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
      function f_handle_eos 't_key'

  s_value
    c_line_break: s_start
      emit t_value
      buffer reset
      buffer write
      emit t_line_break
      buffer reset
    c_eos: s_done
      function f_handle_eos 't_value'
    default: s_value
      buffer write

  s_done

"""
check.register_class(_test_simple_lexer, include_seq = False)
