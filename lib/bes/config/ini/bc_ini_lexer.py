#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from enum import IntFlag

from bes.compat.StringIO import StringIO
from bes.common.string_util import string_util
from bes.common.point import point
from bes.system.log import log
from bes.text.line_break import line_break

from .bc_ini_lexer_token import bc_ini_lexer_token
from .bc_ini_lexer_options import bc_ini_lexer_options
from .bc_ini_error import bc_ini_error

from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_begin
from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_comment
from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_done
from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_double_quoted_string
from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_single_quoted_string
from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_space
from ._detail._bc_ini_lexer_state import _bc_ini_lexer_state_string

class bc_ini_lexer(object):
  TOKEN_COMMENT = 'comment'
  TOKEN_DONE = 'done'
  TOKEN_SPACE = 'space'
  TOKEN_STRING = 'string'
  TOKEN_SECTION_BEGIN = 'section_begin'
  TOKEN_SECTION_END = 'section_end'
  TOKEN_LINE_BREAK = 'line_break'

  EOS = '\0'

  SINGLE_QUOTE_CHAR = '\''
  DOUBLE_QUOTE_CHAR = "\""
  COMMENT_CHAR = ';'

  def __init__(self, log_tag, options, source = None):
    log.add_logging(self, tag = log_tag)

    self._options = options or bc_ini_lexer_options.DEFAULT_OPTIONS
    self._source = source or ''
    self._keep_quotes = (self._options & bc_ini_lexer_options.KEEP_QUOTES) != 0
    self._escape_quotes = (self._options & bc_ini_lexer_options.ESCAPE_QUOTES) != 0
    self._ignore_comments = (self._options & bc_ini_lexer_options.IGNORE_COMMENTS) != 0
    self._buffer = None
    self._is_escaping = False
    self._last_char = None
    
    self.STATE_BEGIN = _bc_ini_lexer_state_begin(self)
    self.STATE_DONE = _bc_ini_lexer_state_done(self)
    self.STATE_STRING = _bc_ini_lexer_state_string(self)
    self.STATE_SPACE = _bc_ini_lexer_state_space(self)
    self.STATE_SINGLE_QUOTED_STRING = _bc_ini_lexer_state_single_quoted_string(self)
    self.STATE_DOUBLE_QUOTED_STRING = _bc_ini_lexer_state_double_quoted_string(self)
    self.STATE_COMMENT = _bc_ini_lexer_state_comment(self)
    self.STATE_SECTION_NAME = _bc_ini_lexer_state_section_name(self)
    self.STATE_LINE_BREAK = _bc_ini_lexer_state_line_break(self)

    self.state = self.STATE_BEGIN

  @property
  def ignore_comments(self):
    return self._ignore_comments
    
  @property
  def is_escaping(self):
    return self._is_escaping

  def _run(self, text):
    self.log_d(f'_run() text=\"{test}\" source={self._source} options={options}')
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
#    yield bc_ini_lexer_token(self.TOKEN_DONE, None, self.position)
      
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
    return bc_ini_lexer_token(self.TOKEN_STRING, self.buffer_value(), self.position)

  def make_token_space(self):
    return bc_ini_lexer_token(self.TOKEN_SPACE, self.buffer_value(), self.position)
      
  def make_token_comment(self):
    return bc_ini_lexer_token(self.TOKEN_COMMENT, self.buffer_value(), self.position)

#  TOKEN_LINE_BREAK = 'line_break'
  
  def make_token_section_begin(self):
    return bc_ini_lexer_token(self.TOKEN_SECTION_BEGIN, '[', self.position)

  def make_token_section_end(self):
    return bc_ini_lexer_token(self.TOKEN_SECTION_END, ']', self.position)

  def make_token_section_line_break(self, lb):
    return bc_ini_lexer_token(self.TOKEN_SECTION_END, lb, self.position)

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

  def raise_error(self, message):
    source_blurb = f'{self._source}:line={self.position.y}:col={self.position.x}'
    raise bc_ini_error(f'{message} - {source_blurb}')
