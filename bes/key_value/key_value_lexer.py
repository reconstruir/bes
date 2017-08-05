#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from StringIO import StringIO
from bes.common import string_util
from bes.text.string_lexer import *

class _state_begin(string_lexer_state):
  def __init__(self, lexer):
    super(_state_begin, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
    new_state = None
    tokens = []
    if not self.lexer.is_escaping and c.isspace():
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
    elif not self.lexer.is_escaping and c == self.lexer.delimiter:
      tokens.append(self.lexer.make_token_delimiter())
      new_state = self.lexer.STATE_BEGIN
    elif not self.lexer.is_escaping and c == self.lexer.COMMENT_CHAR:
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_COMMENT
    elif c == self.lexer.EOS:
      new_state = self.lexer.STATE_DONE
    elif not self.lexer.is_escaping and c == self.lexer.SINGLE_QUOTE_CHAR:
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_SINGLE_QUOTED_STRING
    elif not self.lexer.is_escaping and c == self.lexer.DOUBLE_QUOTE_CHAR:
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_DOUBLE_QUOTED_STRING
    else:
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens
    
class _state_space(string_lexer_state):
  def __init__(self, lexer):
    super(_state_space, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
    new_state = None
    tokens = []
    if c.isspace():
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_SPACE
    elif not self.lexer.is_escaping and c == self.lexer.delimiter:
      tokens.append(self.lexer.make_token_space())
      tokens.append(self.lexer.make_token_delimiter())
      new_state = self.lexer.STATE_BEGIN
    elif not self.lexer.is_escaping and c == self.lexer.COMMENT_CHAR:
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

class _state_string(string_lexer_state):
  def __init__(self, lexer):
    super(_state_string, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
    new_state = None
    tokens = []
    if not self.lexer.is_escaping and c.isspace():
      tokens.append(self.lexer.make_token_string())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
    elif not self.lexer.is_escaping and c == self.lexer.delimiter:
      tokens.append(self.lexer.make_token_string())
      tokens.append(self.lexer.make_token_delimiter())
      new_state = self.lexer.STATE_BEGIN
    elif not self.lexer.is_escaping and c == self.lexer.COMMENT_CHAR:
      tokens.append(self.lexer.make_token_string())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_COMMENT
    elif c == self.lexer.EOS:
      tokens.append(self.lexer.make_token_string())
      new_state = self.lexer.STATE_DONE
    elif not self.lexer.is_escaping and c == self.lexer.SINGLE_QUOTE_CHAR:
      self.lexer.buffer_write_quote(c)
      new_state = self.lexer.STATE_SINGLE_QUOTED_STRING
    elif not self.lexer.is_escaping and c == self.lexer.DOUBLE_QUOTE_CHAR:
      self.lexer.buffer_write_quote(c)
      new_state = self.lexer.STATE_DOUBLE_QUOTED_STRING
    else:
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens

class key_value_lexer(string_lexer):

  TOKEN_DELIMITER = 'delimiter'
  DEFAULT_KV_DELIMITERS = string.whitespace
  
  def __init__(self, delimiter, kv_delimiters, options):
    super(key_value_lexer, self).__init__('key_value_lexer', options)

    assert delimiter
    if not string_util.is_char(delimiter):
      raise RuntimeError('delimiter should be a single character instead of: \"%s\"' % (delimiter))
    
    self._delimiter = delimiter
    self._kv_delimiters = kv_delimiters
    
    self.STATE_BEGIN = _state_begin(self)
    self.STATE_DONE = string_lexer_state_done(self)
    self.STATE_STRING = _state_string(self)
    self.STATE_SPACE = _state_space(self)
    self.STATE_SINGLE_QUOTED_STRING = string_lexer_state_single_quoted_string(self)
    self.STATE_DOUBLE_QUOTED_STRING = string_lexer_state_double_quoted_string(self)
    self.STATE_COMMENT = string_lexer_state_comment(self)

    self.state = self.STATE_BEGIN

  @property
  def is_kv_delimiter(self, c):
    'Return True if c is a valid kv_delimiter.'
    assert string_util.is_char(c)
    return c in self._kv_delimiters

  @property
  def delimiter(self):
    return self._delimiter
    
  @classmethod
  def tokenize(clazz, text, delimiter, kv_delimiters = None, options = None):
    options = options or clazz.DEFAULT_OPTIONS
    kv_delimiters = kv_delimiters or clazz.DEFAULT_KV_DELIMITERS
    return clazz(delimiter, kv_delimiters, options)._run(text)

  def make_token_delimiter(self):
    return self.token(self.TOKEN_DELIMITER, self.delimiter, self.line_number)
