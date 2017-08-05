#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from collections import namedtuple
from StringIO import StringIO
from bes.common import string_util
from bes.system import log

class _state(object):

  def __init__(self, lexer):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (lexer.__class__.__name__, self.name))
    self.lexer = lexer
  
  def handle_char(self, c):
    raise RuntimeError('unhandled handle_char(%c) in state %s' % (self.name))

class _state_begin(_state):
  def __init__(self, lexer):
    super(_state_begin, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
    new_state = None
    tokens = []
    if not self.lexer.is_escaping and c.isspace():
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
    elif self.lexer.has_delimiter() and not self.lexer.is_escaping and c == self.lexer.delimiter:
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
    
class _state_done(_state):
  def __init__(self, lexer):
    super(_state_done, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
  
class _state_space(_state):
  def __init__(self, lexer):
    super(_state_space, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
    new_state = None
    tokens = []
    if c.isspace():
      self.lexer.buffer_write(c)
      new_state = self.lexer.STATE_SPACE
    elif self.lexer.has_delimiter() and not self.lexer.is_escaping and c == self.lexer.delimiter:
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

class _state_string(_state):
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
    elif self.lexer.has_delimiter() and not self.lexer.is_escaping and c == self.lexer.delimiter:
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

class _state_quoted_string_base(_state):
  def __init__(self, lexer, quote_char):
    super(_state_quoted_string_base, self).__init__(lexer)
    self.quote_char = quote_char

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
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

class _state_single_quoted_string(_state_quoted_string_base):
  def __init__(self, lexer):
    super(_state_single_quoted_string, self).__init__(lexer, lexer.SINGLE_QUOTE_CHAR)

class _state_double_quoted_string(_state_quoted_string_base):
  def __init__(self, lexer):
    super(_state_double_quoted_string, self).__init__(lexer, lexer.DOUBLE_QUOTE_CHAR)

class _state_comment(_state):
  def __init__(self, lexer):
    super(_state_comment, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
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

class key_value_lexer(object):

  COMMENT = 'comment'
  DELIMITER = 'delimiter'
  DONE = 'done'
  SPACE = 'space'
  STRING = 'string'

  EOS = '\0'

  SINGLE_QUOTE_CHAR = '\''
  DOUBLE_QUOTE_CHAR = "\""
  COMMENT_CHAR = '#'

  token = namedtuple('token', 'type,value,line_number')

  KEEP_QUOTES = 0x01
  ESCAPE_QUOTES = 0x02
  IGNORE_COMMENTS = 0x04

  DEFAULT_OPTIONS = 0x00
  DEFAULT_KV_DELIMITERS = string.whitespace
  
  def __init__(self, delimiter, kv_delimiters, options):
    log.add_logging(self, tag = 'key_value_lexer')

    assert delimiter
    if delimiter != None and not string_util.is_char(delimiter):
      raise RuntimeError('delimiter should be either None or a single character instead of: \"%s\"' % (delimiter))
    
    self._delimiter = delimiter
    self._kv_delimiters = kv_delimiters
    self._keep_quotes = (options & self.KEEP_QUOTES) != 0

    self._escape_quotes = (options & self.ESCAPE_QUOTES) != 0
    self._ignore_comments = (options & self.IGNORE_COMMENTS) != 0
    self._buffer = None
    self._is_escaping = False
    self._last_char = None
    
    self.STATE_BEGIN = _state_begin(self)
    self.STATE_DONE = _state_done(self)
    self.STATE_STRING = _state_string(self)
    self.STATE_SPACE = _state_space(self)
    self.STATE_SINGLE_QUOTED_STRING = _state_single_quoted_string(self)
    self.STATE_DOUBLE_QUOTED_STRING = _state_double_quoted_string(self)
    self.STATE_COMMENT = _state_comment(self)

    self.state = self.STATE_BEGIN

  @property
  def is_escaping(self):
    return self._is_escaping

  @property
  def is_kv_delimiter(self, c):
    'Return True if c is a valid kv_delimiter.'
    assert string_util.is_char(c)
    return c in self._kv_delimiters

  @property
  def delimiter(self):
    return self._delimiter
    
  def has_delimiter(self):
    return self._delimiter != None

  def _run(self, text):
    self.log_d('tokenize(%s)' % (text))
    assert self.EOS not in text
    self.line_number = 1
    for c in self.__chars_plus_eos(text):
      self._is_escaping = self._last_char == '\\'
      if c != '\\':
        tokens = self.state.handle_char(c)
        for token in tokens:
          self.log_i('tokenize: new token: %s' % (str(token)))
          yield token
      self._last_char = c
      if c == '\n':
        self.line_number += 1
    assert self.state == self.STATE_DONE
    yield self.token(self.DONE, None, self.line_number)
      
  @classmethod
  def tokenize(clazz, text, delimiter, kv_delimiters = None, options = None):
    options = options or clazz.DEFAULT_OPTIONS
    kv_delimiters = kv_delimiters or clazz.DEFAULT_KV_DELIMITERS
    return clazz(delimiter, kv_delimiters, options)._run(text)

  @classmethod
  def char_to_string(clazz, c):
    if c == clazz.EOS:
      return 'EOS'
    else:
      return c
      
  def change_state(self, new_state, c):
    assert new_state
    if new_state == self.state:
      return
    self.log_d('transition: %20s -> %-20s; c="%s"; is_escaping=%s'  % (self.state.__class__.__name__,
                                                                       new_state.__class__.__name__,
                                                                       self.char_to_string(c),
                                                                       self._is_escaping))
    self.state = new_state

  @classmethod
  def __chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS

  def make_token_delimiter(self):
    return self.token(self.DELIMITER, self.delimiter, self.line_number)
      
  def make_token_string(self):
    return self.token(self.STRING, self._buffer.getvalue(), self.line_number)

  def make_token_space(self):
    return self.token(self.SPACE, self._buffer.getvalue(), self.line_number)
      
  def make_token_comment(self):
    return self.token(self.COMMENT, self._buffer.getvalue(), self.line_number)
      
  def buffer_reset(self, c = None):
    self._buffer = StringIO()
    if c:
      self._buffer.write(c)
      
  def buffer_reset_with_quote(self, c):
    assert c in [ self.SINGLE_QUOTE_CHAR, self.DOUBLE_QUOTE_CHAR ]
    self.buffer_reset()
    self.buffer_write_quote(c)
      
  def buffer_write(self, c):
    self._buffer.write(c)

  def buffer_write_quote(self, c):
    assert c in [ self.SINGLE_QUOTE_CHAR, self.DOUBLE_QUOTE_CHAR ]
    if self._keep_quotes:
      if self._escape_quotes:
        self.buffer_write('\\')
      self.buffer_write(c)
