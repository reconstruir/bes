#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from collections import namedtuple
from StringIO import StringIO
from bes.common import string_util
from bes.system import log

class string_lexer_state(object):

  def __init__(self, lexer):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (lexer.__class__.__name__, self.name))
    self.lexer = lexer
  
  def handle_char(self, c):
    raise RuntimeError('unhandled handle_char(%c) in state %s' % (self.name))

class string_lexer_state_begin(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_begin, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
    new_state = None
    tokens = []
    if not self.lexer.is_escaping and c.isspace():
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
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
    
class string_lexer_state_done(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_done, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
  
class string_lexer_state_space(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_space, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
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
    else:
      tokens.append(self.lexer.make_token_space())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_STRING
    self.lexer.change_state(new_state, c)
    return tokens

class string_lexer_state_string(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_string, self).__init__(lexer)

  def handle_char(self, c):
    self.log_d('handle_char(%s)' % (self.lexer.char_to_string(c)))
    new_state = None
    tokens = []
    if not self.lexer.is_escaping and c.isspace():
      tokens.append(self.lexer.make_token_string())
      self.lexer.buffer_reset(c)
      new_state = self.lexer.STATE_SPACE
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

class _state_quoted_string_base(string_lexer_state):
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

class string_lexer_state_single_quoted_string(_state_quoted_string_base):
  def __init__(self, lexer):
    super(string_lexer_state_single_quoted_string, self).__init__(lexer, lexer.SINGLE_QUOTE_CHAR)

class string_lexer_state_double_quoted_string(_state_quoted_string_base):
  def __init__(self, lexer):
    super(string_lexer_state_double_quoted_string, self).__init__(lexer, lexer.DOUBLE_QUOTE_CHAR)

class string_lexer_state_comment(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_comment, self).__init__(lexer)

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

class string_lexer_options(object):
  KEEP_QUOTES = 0x01
  ESCAPE_QUOTES = 0x02
  IGNORE_COMMENTS = 0x04
  DEFAULT_OPTIONS = 0x00

  
class string_lexer(string_lexer_options):

  TOKEN_COMMENT = 'comment'
  TOKEN_DONE = 'done'
  TOKEN_SPACE = 'space'
  TOKEN_STRING = 'string'

  EOS = '\0'

  SINGLE_QUOTE_CHAR = '\''
  DOUBLE_QUOTE_CHAR = "\""
  COMMENT_CHAR = '#'

  token = namedtuple('token', 'type,value,line_number')

  def __init__(self, log_tag, options):
    log.add_logging(self, tag = log_tag)

    options = options or self.DEFAULT_OPTIONS

    self._keep_quotes = (options & self.KEEP_QUOTES) != 0
    self._escape_quotes = (options & self.ESCAPE_QUOTES) != 0
    self._ignore_comments = (options & self.IGNORE_COMMENTS) != 0
    self._buffer = None
    self._is_escaping = False
    self._last_char = None
    
    self.STATE_BEGIN = string_lexer_state_begin(self)
    self.STATE_DONE = string_lexer_state_done(self)
    self.STATE_STRING = string_lexer_state_string(self)
    self.STATE_SPACE = string_lexer_state_space(self)
    self.STATE_SINGLE_QUOTED_STRING = string_lexer_state_single_quoted_string(self)
    self.STATE_DOUBLE_QUOTED_STRING = string_lexer_state_double_quoted_string(self)
    self.STATE_COMMENT = string_lexer_state_comment(self)

    self.state = self.STATE_BEGIN

  @property
  def is_escaping(self):
    return self._is_escaping

  def _run(self, text):
    self.log_d('tokenize(%s)' % (text))
    assert self.EOS not in text
    self.line_number = 1
    for c in self.__chars_plus_eos(text):
      self._is_escaping = self._last_char == '\\'
      should_handle_char = (self._is_escaping and c == '\\') or (c != '\\')
      if should_handle_char:
        tokens = self.state.handle_char(c)
        for token in tokens:
          self.log_i('tokenize: new token: %s' % (str(token)))
          yield token
      self._last_char = c
              
      if c == '\n':
        self.line_number += 1
    assert self.state == self.STATE_DONE
    yield self.token(self.TOKEN_DONE, None, self.line_number)
      
  @classmethod
  def tokenize(clazz, text, log_tag, options = None):
    return clazz(log_tag, options)._run(text)

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

  def make_token_string(self):
    return self.token(self.TOKEN_STRING, self._buffer.getvalue(), self.line_number)

  def make_token_space(self):
    return self.token(self.TOKEN_SPACE, self._buffer.getvalue(), self.line_number)
      
  def make_token_comment(self):
    return self.token(self.TOKEN_COMMENT, self._buffer.getvalue(), self.line_number)
      
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
