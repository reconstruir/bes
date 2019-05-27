#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import string
from collections import namedtuple

from bes.compat import StringIO
from bes.common import string_util, point
from bes.system import log

variable_token = namedtuple('variable_token', 'name, text, default_value, start_pos, end_pos')

class variable_parser(object):
  EOS = '\0'

  def _run(self, text):
    self.log_d('_run() text=\"{}\")'.format(text))
    assert self.EOS not in text
    self.position = point(1, 1)
    for c in self._chars_plus_eos(text):
      self._is_escaping = self._last_char == '\\'
      should_handle_char = (self._is_escaping and c == '\\') or (c != '\\')
      if should_handle_char:
        var = self.state.handle_char(c)
        if var:
          yield var
      self._last_char = c
              
      if c == '\n':
        self.position = point(1, self.position.y + 1)
      else:
        self.position = point(self.position.x + 1, self.position.y)
        
    assert self.state == self.STATE_DONE

  def __init__(self):
    log.add_logging(self, 'variable_parser')

    self._buffer = None
    self._expected_closing_bracket = None
    self._is_escaping = False
    self._last_char = None

    self.STATE_READY = _state_ready(self)
    self.STATE_VARIABLE_BODY = _state_variable_body(self)
    self.STATE_VARIABLE_DEFAULT = _state_variable_default(self)
    self.STATE_BEGIN = _state_begin(self)
    self.STATE_BRACKET_EXPECTING_FIRST_CHAR = _state_bracket_expecting_first_char(self)
    self.STATE_BRACKET_BODY = _state_bracket_body(self)
    self.STATE_DEFAULT_BODY = _state_default_body(self)
    self.STATE_BRACKET_EXPECTING_DASH = _state_bracket_expecting_dash(self)
    self.STATE_DONE = _state_done(self)

    self.state = self.STATE_READY

  @property
  def ignore_comments(self):
    return self._ignore_comments
    
  @property
  def is_escaping(self):
    return self._is_escaping

  @classmethod
  def parse(clazz, text):
    p = variable_parser()
    return p._run(text)

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

  @classmethod
  def is_valid_first_char(clazz, c):
    return c.isalpha() or c == '_'
    
  def is_valid_body_char(clazz, c):
    return clazz.is_valid_first_char(c) or c.isdigit()
      
  def buffer_reset(self, c = None):
    self._buffer = StringIO()
    if c:
      self.buffer_write(c)
      
  def buffer_write(self, c):
    assert c != self.EOS
    self._buffer.write(c)

  def buffer_value(self):
    return self._buffer.getvalue()
    
class _state_base(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_char(self, c):
    raise RuntimeError('unhandled handle_char(%c) in state %s' % (self.name))

  def log_handle_char(self, c):
    try:
      buffer_value = string_util.quote(self.parser.buffer_value())
    except AttributeError as ex:
      buffer_value = 'None'
    self.log_d('handle_char() %s' % (self._make_log_attributes(c)))
  
  def _make_log_attributes(self, c, include_state = True):
    attributes = []
    if include_state:
      attributes.append('state=%s' % (self.name))
    attributes.append('c=|%s|' % (self.parser.char_to_string(c)))
    try:
      attributes.append('buffer=%s' % (string_util.quote(self.parser.buffer_value())))
    except AttributeError as ex:
      attributes.append('buffer=None')
    attributes.append('is_escaping=%s' % (self.parser.is_escaping))
    return ' '.join(attributes)
  
class _state_ready(_state_base):
  def __init__(self, parser):
    super(_state_ready, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    if c == '$' and not self.parser.is_escaping:
      self.parser._start_pos = self.parser.position
      new_state = self.parser.STATE_BEGIN
    elif c == self.parser.EOS:
      new_state = self.parser.STATE_DONE
    else:
      new_state = self.parser.STATE_READY
    self.parser.change_state(new_state, c)
    return None

class _state_begin(_state_base):
  def __init__(self, parser):
    super(_state_begin, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    if c == '{':
      self.parser._expected_closing_bracket = '}'
      new_state = self.parser.STATE_BRACKET_EXPECTING_FIRST_CHAR
    elif c == '(':
      self.parser._expected_closing_bracket = ')'
      new_state = self.parser.STATE_BRACKET_EXPECTING_FIRST_CHAR
    elif self.parser.is_valid_first_char(c):
      self.parser._expected_closing_bracket = None
      self.parser.buffer_reset(c)
      new_state = self.parser.STATE_VARIABLE_BODY
    else:
      raise RuntimeError('{}: unexpected char: "{}"' % (self.name, c))
    self.parser.change_state(new_state, c)
    return None

class _state_bracket_expecting_first_char(_state_base):
  def __init__(self, parser):
    super(_state_bracket_expecting_first_char, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    if self.parser.is_valid_first_char(c):
      self.parser.buffer_reset(c)
      new_state = self.parser.STATE_BRACKET_BODY
    else:
      raise RuntimeError('{}: unexpected char: "{}"' % (self.name, c))
    self.parser.change_state(new_state, c)
    return None

class _state_bracket_body(_state_base):
  def __init__(self, parser):
    super(_state_bracket_body, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    result = None
    if self.parser.is_valid_body_char(c):
      self.parser.buffer_write(c)
      new_state = self.parser.STATE_BRACKET_BODY
    elif c == self.parser._expected_closing_bracket:
      value = self.parser.buffer_value()
      result = variable_token(value, value, None, self.parser._start_pos, self.parser.position)
      new_state = self.parser.STATE_READY
    elif c == ':':
      self.parser._value = self.parser.buffer_value()
      new_state = self.parser.STATE_BRACKET_EXPECTING_DASH
    self.parser.change_state(new_state, c)
    return result
  
class _state_bracket_expecting_dash(_state_base):
  def __init__(self, parser):
    super(_state_bracket_expecting_dash, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    if c == '-':
      self.parser.buffer_reset()
      new_state = self.parser.STATE_DEFAULT_BODY
    elif c == self.parser._expected_closing_bracket:
      value = self.parser.buffer_value()
      print('3 value: {}'.format(value))
      new_state = self.parser.STATE_READY
    self.parser.change_state(new_state, c)
    return None

class _state_default_body(_state_base):
  def __init__(self, parser):
    super(_state_default_body, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    result = None
    if c == self.parser._expected_closing_bracket:
      value = self.parser._value
      default_value = self.parser.buffer_value()
      text = '{}:-{}'.format(value, default_value)
      result = variable_token(value, text, default_value, self.parser._start_pos, self.parser.position)
      new_state = self.parser.STATE_READY
    else:
      self.parser.buffer_write(c)
      new_state = self.parser.STATE_DEFAULT_BODY
    self.parser.change_state(new_state, c)
    return result
  
class _state_variable_body(_state_base):
  def __init__(self, parser):
    super(_state_variable_body, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    result = None
    if self.parser.is_valid_body_char(c):
      self.parser.buffer_write(c)
      new_state = self.parser.STATE_VARIABLE_BODY
    elif c == self.parser.EOS:
      value = self.parser.buffer_value()
      result = variable_token(value, value, None, self.parser._start_pos, self.parser.position.move(-1, 0))
      new_state = self.parser.STATE_DONE
    else:
      value = self.parser.buffer_value()
      result = variable_token(value, value, None, self.parser._start_pos, self.parser.position.move(-1, 0))
      new_state = self.parser.STATE_READY
    self.parser.change_state(new_state, c)
    return result

class _state_variable_default(_state_base):
  def __init__(self, parser):
    super(_state_variable_default, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
    new_state = None
    if self.parser.is_valid_body_char(c):
      self.parser.buffer_write(c)
      new_state = self.parser.STATE_VARIABLE_BODY
    elif c == self.parser._expected_closing_bracket:
      raise RuntimeError('{}: unexpected char: "{}"' % (self.name, c))
    self.parser.change_state(new_state, c)
    return None

class _state_done(_state_base):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_char(self, c):
    self.log_handle_char(c)
