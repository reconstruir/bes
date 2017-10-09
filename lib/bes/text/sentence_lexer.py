#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from .string_lexer import *

class _state_begin(string_lexer_state):
  def __init__(self, lexer):
    super(_state_begin, self).__init__(lexer)

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
    elif c == self.lexer.COMMENT_CHAR:
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
    elif c in string.punctuation:
      tokens.append(self.lexer.make_token_punctuation(c))
      new_state = self.lexer.STATE_BEGIN
    else:
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens
    
class _state_space(string_lexer_state):
  def __init__(self, lexer):
    super(_state_space, self).__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    tokens = []
      
    if c.isspace():
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_SPACE
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
    elif not self.lexer.is_escaping and c in string.punctuation:
      tokens.append(self.lexer.make_token_space())
      tokens.append(self.lexer.make_token_punctuation(c))
      self.lexer.buffer_reset()
      new_state = self.lexer.STATE_BEGIN
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
    elif c == self.lexer.COMMENT_CHAR:
      tokens.append(self.lexer.make_token_string())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_COMMENT
    elif c == self.lexer.SINGLE_QUOTE_CHAR:
      self.lexer.buffer_write_quote(c)
      new_state = self.lexer.STATE_SINGLE_QUOTED_STRING
    elif c == self.lexer.DOUBLE_QUOTE_CHAR:
      self.lexer.buffer_write_quote(c)
      new_state = self.lexer.STATE_DOUBLE_QUOTED_STRING
    elif not self.lexer.is_escaping and c in string.punctuation:
      tokens.append(self.lexer.make_token_string())
      tokens.append(self.lexer.make_token_punctuation(c))
      self.lexer.buffer_reset()
      new_state = self.lexer.STATE_BEGIN
    else:
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens

'''  
class _state_punctuation(string_lexer_state):
  def __init__(self, lexer):
    super(_state_punctuation, self).__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    tokens = []

#    if self.lexer.is_escaping:
#      raise RuntimeError('Should not escape punctuation: %s' % (c))
    
    if not self.lexer.is_escaping and c.isspace():
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
    elif not self.lexer.is_escaping and c == self.lexer.COMMENT_CHAR:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_COMMENT
    elif c == self.lexer.EOS:
      tokens.append(self.lexer.make_token_punctuation())
      new_state = self.lexer.STATE_DONE
    elif not self.lexer.is_escaping and c == self.lexer.SINGLE_QUOTE_CHAR:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_SINGLE_QUOTED_STRING
    elif not self.lexer.is_escaping and c == self.lexer.DOUBLE_QUOTE_CHAR:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset_with_quote(c)
      new_state = self.lexer.STATE_DOUBLE_QUOTED_STRING
    elif not self.lexer.is_escaping and c in string.punctuation:
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_PUNCTUATION
    else:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens
'''

class sentence_lexer(string_lexer):

  TOKEN_PUNCTUATION = 'punctuation'

  def __init__(self, options):
    super(sentence_lexer, self).__init__('sentence_lexer', options)

    self.STATE_BEGIN = _state_begin(self)
    self.STATE_DONE = string_lexer_state_done(self)
    self.STATE_STRING = _state_string(self)
    self.STATE_SPACE = _state_space(self)
    self.STATE_SINGLE_QUOTED_STRING = string_lexer_state_single_quoted_string(self)
    self.STATE_DOUBLE_QUOTED_STRING = string_lexer_state_double_quoted_string(self)
    self.STATE_COMMENT = string_lexer_state_comment(self)
#    self.STATE_PUNCTUATION = _state_punctuation(self)

    self.state = self.STATE_BEGIN

  @classmethod
  def tokenize(clazz, text, options = None):
    return clazz(options)._run(text)

  def make_token_punctuation(self, c):
    return self.token(self.TOKEN_PUNCTUATION, c, self.line_number)
