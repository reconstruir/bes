#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

# FIXME: add an exception class that handles all the state info attributes
from bes.compat import StringIO
from bes.system import log
from bes.text import line_numbers, string_lexer_options, sentence_lexer as lexer
from .key_value import key_value

class key_value_parser(string_lexer_options.CONSTANTS):

  def __init__(self, options, delimiter, empty_value, log_tag):
    log.add_logging(self, tag = log_tag or 'key_value_parser')
    self._options = options
    self.delimiter = delimiter
    self.empty_value = empty_value
    self._buffer = None
    
    self.STATE_EXPECTING_KEY = _state_expecting_key(self)
    self.STATE_EXPECTING_DELIMITER = _state_expecting_delimiter(self)
    self.STATE_VALUE = _state_value(self)
    self.STATE_DONE = _state_done(self)
    self.state = self.STATE_EXPECTING_KEY
    self.key = None

  def _run(self, text):
    self.log_d('_run() text=\"%s\" options=%s)' % (text, str(string_lexer_options(self._options))))
    self.text = text

    for token in lexer.tokenize(text, 'key_value_lexer', options = self._options):
      key_value = self.state.handle_token(token)
      if key_value:
        self.log_i('parse: new key_value: %s' % (str(key_value)))
        yield key_value
    assert self.state == self.STATE_DONE
      
  def _change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state

  def _token_is_delimiter(self, token):
    assert token.token_type == lexer.TOKEN_PUNCTUATION
    return token.value == self.delimiter

  def _buffer_reset(self, text = None):
    self._buffer = StringIO()
    if text:
      self._buffer_write(text)
  
  def _buffer_write(self, text):
    assert text is not None
    assert self._buffer
    self._buffer.write(text)

  def _buffer_value(self):
    if not self._buffer:
      return self.empty_value
    return self._buffer.getvalue()

  @classmethod
  def parse(clazz, text, options = 0, delimiter = '=', empty_value = None, log_tag = None):
    return clazz(options, delimiter, empty_value, log_tag)._run(text)

  @classmethod
  def parse_to_dict(clazz, text, options = 0, delimiter = '=', empty_value = None, log_tag = None):
    result = {}
    for kv in clazz.parse(text, options = options, delimiter = delimiter,
                          empty_value = empty_value, log_tag = log_tag):
      result[kv.key] = kv.value
    return result

  @classmethod
  def parse_to_list(clazz, text, options = 0, delimiter = '=', empty_value = None, log_tag = None):
    result = []
    for kv in clazz.parse(text, options = options, delimiter = delimiter,
                          empty_value = empty_value, log_tag = log_tag):
      result.append(kv)
    return result

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_token(self, token):
    raise RuntimeError('unhandled handle_token(%c) in state %s' % (self.name))

  def change_state(self, new_state, token):
    self.parser._change_state(new_state, 'token="%s:%s"'  % (token.token_type, token.value))

  def unexpected_token(self, token, expected_label):
    text_blurb = line_numbers.add_line_numbers(self.parser.text)
    raise RuntimeError('unexpected token \"%s:%s\" instead of \"%s\" at line %d:\n%s' % (token.token_type,
                                                                                         token.value,
                                                                                         expected_label,
                                                                                         token.position.y,
                                                                                         text_blurb))
  
class _state_expecting_key(_state):
  def __init__(self, parser):
    super(_state_expecting_key, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    if token.token_type == lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.token_type == lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.token_type == lexer.TOKEN_PUNCTUATION:
      self.unexpected_token(token, 'key')
    elif token.token_type == lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
    elif token.token_type == lexer.TOKEN_STRING:
      self.parser.key = token.value
      new_state = self.parser.STATE_EXPECTING_DELIMITER
    self.change_state(new_state, token)
    return None
    
class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    if token.token_type != lexer.TOKEN_DONE:
      self.unexpected_token(token, 'done')
    self.change_state(self.parser.STATE_DONE, token)
    return None
  
class _state_expecting_delimiter(_state):
  def __init__(self, parser):
    super(_state_expecting_delimiter, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.token_type == lexer.TOKEN_COMMENT:
      key_value_result = key_value(self.parser.key, self.parser.empty_value)
      new_state = self.parser.STATE_DONE
    elif token.token_type == lexer.TOKEN_SPACE:
      self.unexpected_token(token, 'delimiter')
    elif token.token_type == lexer.TOKEN_PUNCTUATION:
      if not self.parser._token_is_delimiter(token):
        self.unexpected_token(token, 'delimiter:%s' % (self.parser.delimiter))
      new_state = self.parser.STATE_VALUE
    elif token.token_type == lexer.TOKEN_DONE:
      self.unexpected_token(token, 'delimiter:%s' % (self.parser.delimiter))
    elif token.token_type == lexer.TOKEN_STRING:
      self.unexpected_token(token, 'delimiter:%s' % (self.parser.delimiter))
    self.change_state(new_state, token)
    return key_value_result

class _state_value(_state):
  def __init__(self, parser):
    super(_state_value, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.token_type == lexer.TOKEN_COMMENT:
      key_value_result = key_value(self.parser.key, self.parser._buffer_value())
      new_state = self.parser.STATE_DONE
    elif token.token_type == lexer.TOKEN_SPACE:
      key_value_result = key_value(self.parser.key, self.parser._buffer_value())
      self.parser._buffer = None
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.token_type == lexer.TOKEN_PUNCTUATION:
      if self.parser._token_is_delimiter(token):
        self.unexpected_token(token, 'value')
      else:
        if not self.parser._buffer:
          self.parser._buffer_reset()
        self.parser._buffer_write(token.value)
      new_state = self.parser.STATE_VALUE
    elif token.token_type == lexer.TOKEN_DONE:
      value = self.parser._buffer_value()
      key_value_result = key_value(self.parser.key, self.parser._buffer_value())
      new_state = self.parser.STATE_DONE
    elif token.token_type == lexer.TOKEN_STRING:
#      key_value_result = key_value(self.parser.key, token.value)
      if not self.parser._buffer:
        self.parser._buffer_reset()
      self.parser._buffer_write(token.value)
      new_state = self.parser.STATE_VALUE
    self.change_state(new_state, token)
    return key_value_result
