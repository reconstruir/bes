#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from bes.compat import StringIO
from bes.common import string_util, point
from bes.system import log
from bes.enum import flag_enum
from .lexer_token import lexer_token

class string_lexer_options(flag_enum):
  KEEP_QUOTES = 0x01
  ESCAPE_QUOTES = 0x02
  IGNORE_COMMENTS = 0x04
  DEFAULT_OPTIONS = 0x00
  
class string_lexer(string_lexer_options.CONSTANTS):
  TOKEN_COMMENT = 'comment'
  TOKEN_DONE = 'done'
  TOKEN_SPACE = 'space'
  TOKEN_STRING = 'string'

  EOS = '\0'

  SINGLE_QUOTE_CHAR = '\''
  DOUBLE_QUOTE_CHAR = "\""
  COMMENT_CHAR = '#'

  def __init__(self, log_tag, options):
    log.add_logging(self, tag = log_tag)

    self._options = options or self.DEFAULT_OPTIONS
    self._keep_quotes = (self._options & self.KEEP_QUOTES) != 0
    self._escape_quotes = (self._options & self.ESCAPE_QUOTES) != 0
    self._ignore_comments = (self._options & self.IGNORE_COMMENTS) != 0
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
  def ignore_comments(self):
    return self._ignore_comments
    
  @property
  def is_escaping(self):
    return self._is_escaping

  def _run(self, text):
    self.log_d('_run() text=\"%s\" options=%s)' % (text, str(string_lexer_options(self._options))))
    assert self.EOS not in text
    self.position = point(1, 1)
    for c in self._chars_plus_eos(text):
      self._is_escaping = self._last_char == '\\'
      should_handle_char = (self._is_escaping and c == '\\') or (c != '\\')
      if should_handle_char:
        tokens = self.state.handle_char(c)
        for token in tokens:
          self.log_d('tokenize: new token: %s' % (str(token)))
          yield token
      self._last_char = c
              
      if c == '\n':
        self.position = point(1, self.position.y + 1)
      else:
        self.position = point(self.position.x + 0, self.position.y)
        
    assert self.state == self.STATE_DONE
    yield lexer_token(self.TOKEN_DONE, None, self.position)
      
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
    self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__,
                                                   new_state.__class__.__name__,
                                                   new_state._make_log_attributes(c, include_state = False)))
    self.state = new_state

  @classmethod
  def _chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS

  def make_token_string(self):
    return lexer_token(self.TOKEN_STRING, self.buffer_value(), self.position)

  def make_token_space(self):
    return lexer_token(self.TOKEN_SPACE, self.buffer_value(), self.position)
      
  def make_token_comment(self):
    return lexer_token(self.TOKEN_COMMENT, self.buffer_value(), self.position)
      
  def buffer_reset(self, c = None):
    self._buffer = StringIO()
    if c:
      self.buffer_write(c)
      
  def buffer_reset_with_quote(self, c):
    assert c in [ self.SINGLE_QUOTE_CHAR, self.DOUBLE_QUOTE_CHAR ]
    self.buffer_reset()
    self.buffer_write_quote(c)
      
  def buffer_write(self, c):
    assert c != self.EOS
    self._buffer.write(c)

  def buffer_value(self):
    return self._buffer.getvalue()
    
  def buffer_write_quote(self, c):
    assert c in [ self.SINGLE_QUOTE_CHAR, self.DOUBLE_QUOTE_CHAR ]
    if self._keep_quotes:
      if self._escape_quotes:
        self.buffer_write('\\')
      self.buffer_write(c)

class string_lexer_state(object):

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
  
class string_lexer_state_begin(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_begin, self).__init__(lexer)

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
    
class string_lexer_state_done(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_done, self).__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
  
class string_lexer_state_space(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_space, self).__init__(lexer)

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

class string_lexer_state_string(string_lexer_state):
  def __init__(self, lexer):
    super(string_lexer_state_string, self).__init__(lexer)

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

class _state_quoted_string_base(string_lexer_state):
  def __init__(self, lexer, quote_char):
    super(_state_quoted_string_base, self).__init__(lexer)
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
