#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.common.string_util import string_util
from bes.system.log import log

class _bc_ini_lexer_state(object):

  def __init__(self, lexer):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (lexer.__class__.__name__, self.name))
    self.lexer = lexer
  
  def handle_char(self, c):
    raise RuntimeError('unhandled handle_char(%c) in state %s' % (self.name))

  def log_handle_char(self, c):
    try:
      buffer_value = string_util.quote(self.lexer.buffer_value())
    except AttributeError as ex:
      buffer_value = 'None'
    self.log_d('handle_char() %s' % (self._make_log_attributes(c)))
  
  def _make_log_attributes(self, c, include_state = True):
    attributes = []
    if include_state:
      attributes.append('state=%s' % (self.name))
    attributes.append('c=|%s|' % (self.lexer.char_to_string(c)))
    try:
      attributes.append('buffer=%s' % (string_util.quote(self.lexer.buffer_value())))
    except AttributeError as ex:
      attributes.append('buffer=None')
    attributes.append('is_escaping=%s' % (self.lexer.is_escaping))
    return ' '.join(attributes)
  
class _bc_ini_lexer_state_begin(_bc_ini_lexer_state):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    tokens = []
    if self.lexer.is_escaping:
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_STRING
    elif c.isspace():
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
    elif c == self.lexer.COMMENT_CHAR and not self.lexer.ignore_comments:
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_COMMENT
    elif c == self.lexer.EOS:
      new_state = self.lexer.STATE_DONE
    elif c == self.lexer.SINGLE_QUOTE_CHAR:
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_SINGLE_QUOTED_STRING
    elif c == self.lexer.DOUBLE_QUOTE_CHAR:
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_DOUBLE_QUOTED_STRING
    else:
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens
    
class _bc_ini_lexer_state_done(_bc_ini_lexer_state):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
  
class _bc_ini_lexer_state_space(_bc_ini_lexer_state):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    tokens = []
    if c.isspace():
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_SPACE
    elif not self.lexer.is_escaping and (c == self.lexer.COMMENT_CHAR and not self.lexer.ignore_comments):
      tokens.append(self.lexer.make_token_space())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_COMMENT
    elif c == self.lexer.EOS:
      tokens.append(self.lexer.make_token_space())
      new_state = self.lexer.STATE_DONE
    elif not self.lexer.is_escaping and c == self.lexer.SINGLE_QUOTE_CHAR:
      tokens.append(self.lexer.make_token_space())
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_SINGLE_QUOTED_STRING
    elif not self.lexer.is_escaping and c == self.lexer.DOUBLE_QUOTE_CHAR:
      tokens.append(self.lexer.make_token_space())
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_DOUBLE_QUOTED_STRING
    else:
      tokens.append(self.lexer.make_token_space())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens

class _bc_ini_lexer_state_string(_bc_ini_lexer_state):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    tokens = []
    if c == self.lexer.EOS:
      tokens.append(self.lexer.make_token_string())
      new_state = self.lexer.STATE_DONE
    elif self.lexer.is_escaping:
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_STRING
    elif c.isspace():
      tokens.append(self.lexer.make_token_string())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
    elif c == self.lexer.COMMENT_CHAR and not self.lexer.ignore_comments:
      tokens.append(self.lexer.make_token_string())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_COMMENT
    elif c == self.lexer.SINGLE_QUOTE_CHAR:
      self.lexer.buffer_write_quote(c)
      new_state = self.lexer.STATE_SINGLE_QUOTED_STRING
    elif c == self.lexer.DOUBLE_QUOTE_CHAR:
      self.lexer.buffer_write_quote(c)
      new_state = self.lexer.STATE_DOUBLE_QUOTED_STRING
    else:
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens

class _bc_ini_lexer_state_quoted_string_base(_bc_ini_lexer_state):
  def __init__(self, lexer, quote_char):
    super().__init__(lexer)
    self.quote_char = quote_char

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    tokens = []
    if c == self.lexer.EOS:
      raise RuntimeError('unexpected done of string waiting for: %s' % (self.quote_char))
    elif not self.lexer.is_escaping and c == self.quote_char:
      self.lexer.buffer_write_quote(c)
      tokens.append(self.lexer.make_token_string())
      new_state = self.lexer.STATE_BEGIN
    else:
      self.lexer.buffer_write(c)
      new_state = self.lexer.state
    self.lexer.change_state(new_state, c)
    return tokens

class _bc_ini_lexer_state_single_quoted_string(_bc_ini_lexer_state_quoted_string_base):
  def __init__(self, lexer):
    super().__init__(lexer, lexer.SINGLE_QUOTE_CHAR)

class _bc_ini_lexer_state_double_quoted_string(_bc_ini_lexer_state_quoted_string_base):
  def __init__(self, lexer):
    super().__init__(lexer, lexer.DOUBLE_QUOTE_CHAR)

class _bc_ini_lexer_state_comment(_bc_ini_lexer_state):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    tokens = []
    if c == self.lexer.EOS:
      tokens.append(self.lexer.make_token_comment())
      new_state = self.lexer.STATE_DONE
    else:
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_COMMENT
    self.lexer.change_state(new_state, c)
    return tokens
