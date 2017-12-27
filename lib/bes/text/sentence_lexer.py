#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from .string_lexer import *
from .lexer_token import lexer_token

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
    elif self.lexer.is_punctuation(c):
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
    elif not self.lexer.is_escaping and self.lexer.is_punctuation(c):
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
    elif not self.lexer.is_escaping and self.lexer.is_punctuation(c):
      tokens.append(self.lexer.make_token_string())
      tokens.append(self.lexer.make_token_punctuation(c))
      self.lexer.buffer_reset()
      new_state = self.lexer.STATE_BEGIN
    else:
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens

class sentence_lexer(string_lexer):

  TOKEN_PUNCTUATION = 'punctuation'

  _PUNCTUATION_CHARS = [ c for c in string.punctuation if c not in [ '_' ] ]
  
  def __init__(self, log_tag, options):
    super(sentence_lexer, self).__init__(log_tag, options)

    self.STATE_BEGIN = _state_begin(self)
    self.STATE_DONE = string_lexer_state_done(self)
    self.STATE_STRING = _state_string(self)
    self.STATE_SPACE = _state_space(self)
    self.STATE_SINGLE_QUOTED_STRING = string_lexer_state_single_quoted_string(self)
    self.STATE_DOUBLE_QUOTED_STRING = string_lexer_state_double_quoted_string(self)
    self.STATE_COMMENT = string_lexer_state_comment(self)

    self.state = self.STATE_BEGIN

  @classmethod
  def tokenize(clazz, text, log_tag = 'sentence_lexer', options = None):
    return clazz(log_tag, options)._run(text)

  def make_token_punctuation(self, c):
    return lexer_token(self.TOKEN_PUNCTUATION, c, self.position)

  @classmethod
  def is_punctuation(clazz, c):
    return c in clazz._PUNCTUATION_CHARS
  
