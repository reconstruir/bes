#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from collections import namedtuple
from enum import IntEnum

from bes.compat.StringIO import StringIO
from bes.common.string_util import string_util
from bes.common.point import point
from bes.system.log import log
from bes.text.lexer_token import lexer_token
from ..text.text_lexer_state_base import text_lexer_state_base

from .semantic_version_error import semantic_version_error

class semantic_version_lexer(object):

  TOKEN_DONE = 'done'
  TOKEN_PART = 'part'
  TOKEN_PART_DELIMITER = 'part_delimiter'
  TOKEN_PUNCTUATION = 'punctuation'
  TOKEN_SPACE = 'space'
  TOKEN_STRING = 'string'
  TOKEN_TEXT = 'text'

  EOS = '\0'

  def __init__(self, log_tag):
    log.add_logging(self, tag = log_tag)

    self._buffer = None
    
    self.STATE_BEGIN = _state_begin(self)
    self.STATE_DONE = _state_done(self)
    self.STATE_PART = _state_part(self)
    self.STATE_PART_DELIMITER = _state_part_delimiter(self)
    self.STATE_PUNCTUATION = _state_punctuation(self)
    self.STATE_TEXT = _state_text(self)

    self.state = self.STATE_BEGIN

  def _run(self, text):
    self.log_d('_run() text=\"%s\")' % (text))
    assert self.EOS not in text
    self.text = text
    self.position = point(-1, 0)
    for c in self._chars_plus_eos(text):
      cr = self._char_type(c)
      if cr.ctype == self._lexer_char_types.UNKNOWN:
        raise semantic_version_error('unknown character: \"%s\"' % (c))
      tokens = self.state.handle_char(cr)
      for token in tokens:
        self.log_d('tokenize: new token: %s' % (str(token)))
        yield token
      self.position = self.position.move(1, 0)
    assert self.state == self.STATE_DONE
    yield lexer_token(self.TOKEN_DONE, None, self.position)
      
  @classmethod
  def tokenize(clazz, text, log_tag):
    return clazz(log_tag)._run(text)

  @classmethod
  def _char_to_string(clazz, c):
    if c == clazz.EOS:
      return 'EOS'
    else:
      return c
  
  def change_state(self, new_state, cr):
    assert new_state
    if new_state == self.state:
      return
    self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__,
                                                   new_state.__class__.__name__,
                                                   new_state._make_log_attributes(cr, include_state = False)))
    self.state = new_state

  @classmethod
  def _chars_plus_eos(self, text):
    for c in text:
      yield c
    yield self.EOS

  def make_token_text(self):
    value = self.buffer_value()
    offset = len(value) - 1
    position = self.position.clone(mutations = { 'x': self.position.x - offset })
    return lexer_token(self.TOKEN_TEXT, self.buffer_value(), position)
      
  def make_token_part(self):
    value = self.buffer_value()
    offset = len(value) - 1
    position = self.position.clone(mutations = { 'x': self.position.x - offset })
    return lexer_token(self.TOKEN_PART, int(value), position)
      
  def make_token_punctuation(self):
    value = self.buffer_value()
    offset = len(value) - 1
    position = self.position.clone(mutations = { 'x': self.position.x - offset })
    return lexer_token(self.TOKEN_PUNCTUATION, value, position)
      
  def make_token_part_delimiter(self):
    return lexer_token(self.TOKEN_PART_DELIMITER, self.buffer_value(), self.position)
      
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

  class _lexer_char_types(IntEnum):
    EOS = 1
    PART = 2
    PART_DELIMITER = 3
    PUNCTUATION = 4
    TEXT = 5
    UNKNOWN = 6

  _char_result = namedtuple('_char_result', 'char, ctype')

  _PART_DELIMITER_CHARS = set('.-,:;_')
  _PUNCTUATION_CHARS = set(string.punctuation) - _PART_DELIMITER_CHARS
  
  @classmethod
  def _char_type(clazz, c):
    if c in clazz._PART_DELIMITER_CHARS:
      return clazz._char_result(clazz._char_to_string(c), clazz._lexer_char_types.PART_DELIMITER)
    elif c in clazz._PUNCTUATION_CHARS:
      return clazz._char_result(clazz._char_to_string(c), clazz._lexer_char_types.PUNCTUATION)
    elif c.isdigit():
      return clazz._char_result(clazz._char_to_string(c), clazz._lexer_char_types.PART)
    elif c.isalpha():
      return clazz._char_result(clazz._char_to_string(c), clazz._lexer_char_types.TEXT)
    elif c == clazz.EOS:
      return clazz._char_result(clazz._char_to_string(c), clazz._lexer_char_types.EOS)
    else:
      return clazz._char_result(clazz._char_to_string(c), clazz._lexer_char_types.UNKNOWN)
      
class _state(text_lexer_state_base):

  def __init__(self, lexer):
    super().__init__(lexer)

  def _raise_unexpected_char_error(self, cr):
    assert isinstance(cr, self.lexer._char_result)
    msg = '"{}" - unexpected char "{}" in state "{}"'.format(self.lexer.text,
                                                             cr.char,
                                                             self.lexer.state.__class__.__name__)
    raise semantic_version_error(msg, position = self.lexer.position.move(1, 0))
  
class _state_begin(_state):
  def __init__(self, lexer):
    super(_state_begin, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._lexer_char_types.TEXT:
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._lexer_char_types.PART:
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PART
    elif cr.ctype == self.lexer._lexer_char_types.PUNCTUATION:
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._lexer_char_types.EOS:
      new_state = self.lexer.STATE_DONE
    else:
      self._raise_unexpected_char_error(cr)
    self.lexer.change_state(new_state, cr)
    return tokens

class _state_part(_state):
  def __init__(self, lexer):
    super(_state_part, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._lexer_char_types.TEXT:
      tokens.append(self.lexer.make_token_part())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._lexer_char_types.PART:
      self.lexer.buffer_write(cr.char)
      new_state = self.lexer.STATE_PART
    elif cr.ctype == self.lexer._lexer_char_types.PART_DELIMITER:
      tokens.append(self.lexer.make_token_part())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PART_DELIMITER
    elif cr.ctype == self.lexer._lexer_char_types.PUNCTUATION:
      tokens.append(self.lexer.make_token_part())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._lexer_char_types.EOS:
      tokens.append(self.lexer.make_token_part())
      new_state = self.lexer.STATE_DONE
    else:
      self._raise_unexpected_char_error(cr)
    self.lexer.change_state(new_state, cr)
    return tokens

class _state_text(_state):
  def __init__(self, lexer):
    super(_state_text, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._lexer_char_types.TEXT:
      self.lexer.buffer_write(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._lexer_char_types.PART:
      tokens.append(self.lexer.make_token_text())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PART
    elif cr.ctype in ( self.lexer._lexer_char_types.PUNCTUATION, self.lexer._lexer_char_types.PART_DELIMITER ):
      tokens.append(self.lexer.make_token_text())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._lexer_char_types.EOS:
      tokens.append(self.lexer.make_token_text())
      new_state = self.lexer.STATE_DONE
    else:
      self._raise_unexpected_char_error(cr)
    self.lexer.change_state(new_state, cr)
    return tokens

class _state_punctuation(_state):
  def __init__(self, lexer):
    super(_state_punctuation, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._lexer_char_types.TEXT:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_TEXT
    elif cr.ctype == self.lexer._lexer_char_types.PART:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PART
    elif cr.ctype == self.lexer._lexer_char_types.PUNCTUATION:
      self.lexer.buffer_write(cr.char)
      new_state = self.lexer.STATE_PUNCTUATION
    elif cr.ctype == self.lexer._lexer_char_types.EOS:
      tokens.append(self.lexer.make_token_punctuation())
      new_state = self.lexer.STATE_DONE
    else:
      self._raise_unexpected_char_error(cr)
    self.lexer.change_state(new_state, cr)
    return tokens
  
class _state_part_delimiter(_state):
  def __init__(self, lexer):
    super(_state_part_delimiter, self).__init__(lexer)

  def handle_char(self, cr):
    self.log_handle_char(cr)
    new_state = None
    tokens = []
    if cr.ctype == self.lexer._lexer_char_types.PART:
      tokens.append(self.lexer.make_token_part_delimiter())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_PART
    elif cr.ctype == self.lexer._lexer_char_types.TEXT:
      tokens.append(self.lexer.make_token_punctuation())
      self.lexer.buffer_reset(cr.char)
      new_state = self.lexer.STATE_TEXT
    else:
      self._raise_unexpected_char_error(cr)
    self.lexer.change_state(new_state, cr)
    return tokens
  
class _state_done(_state):
  def __init__(self, lexer):
    super(_state_done, self).__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)
