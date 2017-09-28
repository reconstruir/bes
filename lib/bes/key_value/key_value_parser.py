#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from bes.text import line_numbers, string_lexer_options
from .key_value_lexer import key_value_lexer as lexer
from .key_value import key_value

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_token(self, token):
    raise RuntimeError('unhandled handle_token(%c) in state %s' % (self.name))

  def change_state(self, new_state, token):
    self.parser.change_state(new_state, 'token="%s:%s"'  % (token.type, token.value))

class _state_expecting_key(_state):
  def __init__(self, parser):
    super(_state_expecting_key, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    if token.type == lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.type == lexer.TOKEN_DELIMITER:
      raise RuntimeError('unexpected delimiter instead of key: %s' % (self.parser.text))
    elif token.type == lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.TOKEN_STRING:
      self.parser.key = token.value
      new_state = self.parser.STATE_EXPECTING_DELIMITER
    self.change_state(new_state, token)
    
class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    if token.type != lexer.TOKEN_DONE:
      raise RuntimeError('unexpected token in done state: %s' % (str(token)))
    self.change_state(self.parser.STATE_DONE, token)
  
class _state_expecting_delimiter(_state):
  def __init__(self, parser):
    super(_state_expecting_delimiter, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.type == lexer.TOKEN_COMMENT:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.TOKEN_SPACE:
      raise RuntimeError('unexpected space instead of \"%s\" at line %d:\n%s' % (self.parser.delimiter,
                                                                                 token.line_number,
                                                                                 line_numbers.add_line_numbers(self.parser.text)))
    elif token.type == lexer.TOKEN_DELIMITER:
      new_state = self.parser.STATE_EXPECTING_VALUE
    elif token.type == lexer.TOKEN_DONE:
      raise RuntimeError('unexpected done instead of delimiter: %s' % (self.parser.text))
    elif token.type == lexer.TOKEN_STRING:
      raise RuntimeError('unexpected string instead of delimiter: %s' % (self.parser.text))
    self.change_state(new_state, token)
    return key_value_result

class _state_expecting_value(_state):
  def __init__(self, parser):
    super(_state_expecting_value, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.type == lexer.TOKEN_COMMENT:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.TOKEN_SPACE:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.type == lexer.TOKEN_DELIMITER:
      raise RuntimeError('unexpected delimiter instead of string: %s' % (self.parser.text))
    elif token.type == lexer.TOKEN_DONE:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.TOKEN_STRING:
      key_value_result = key_value(self.parser.key, token.value)
      new_state = self.parser.STATE_EXPECTING_KEY
    self.change_state(new_state, token)
    return key_value_result
    
class key_value_parser(string_lexer_options):

  DEFAULT_EMPTY_VALUE = None

  def __init__(self, options, delimiter):
    log.add_logging(self, tag = 'key_value_parser')
    self._options = options
    self.delimiter = delimiter
    
    self.STATE_EXPECTING_KEY = _state_expecting_key(self)
    self.STATE_EXPECTING_DELIMITER = _state_expecting_delimiter(self)
    self.STATE_EXPECTING_VALUE = _state_expecting_value(self)
    self.STATE_DONE = _state_done(self)
    self.state = self.STATE_EXPECTING_KEY
    self.key = None
    
  def run(self, text):
    self.log_d('run(%s)' % (text))
    self.text = text

    for token in lexer.tokenize(text, self.delimiter, options = self._options):
      key_value = self.state.handle_token(token)
      if key_value:
        self.log_i('parse: new key_value: %s' % (str(key_value)))
        yield key_value
    assert self.state == self.STATE_DONE
      
  @classmethod
  def parse(clazz, text, options = 0, delimiter = '='):
    return clazz(options, delimiter).run(text)

  @classmethod
  def parse_to_dict(clazz, text, options = 0):
    result = {}
    for kv in clazz.parse(text, options = options):
      result[kv.key] = kv.value
    return result

  @classmethod
  def parse_to_list(clazz, text, options = 0):
    result = []
    for kv in clazz.parse(text, options = options):
      result.append(kv)
    return result

  def change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state
