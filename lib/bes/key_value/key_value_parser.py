#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from key_value_lexer import key_value_lexer as lexer
from key_value import key_value

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
    if token.type == lexer.COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.SPACE:
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.type == lexer.DELIMITER:
      raise RuntimeError('unexpected equal instead of key: %s' % (self.parser.text))
    elif token.type == lexer.DONE:
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.STRING:
      self.parser.key = token.value
      new_state = self.parser.STATE_EXPECTING_EQUAL
    self.change_state(new_state, token)
    
class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    if token.type != lexer.DONE:
      raise RuntimeError('unexpected token in done state: %s' % (str(token)))
    self.change_state(self.parser.STATE_DONE, token)
  
class _state_expecting_equal(_state):
  def __init__(self, parser):
    super(_state_expecting_equal, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.type == lexer.COMMENT:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.SPACE:
      raise RuntimeError('unexpected space instead of equal: %s' % (self.parser.text))
    elif token.type == lexer.DELIMITER:
      new_state = self.parser.STATE_EXPECTING_VALUE
    elif token.type == lexer.DONE:
      raise RuntimeError('unexpected done instead of equal: %s' % (self.parser.text))
    elif token.type == lexer.STRING:
      raise RuntimeError('unexpected string instead of equal: %s' % (self.parser.text))
    self.change_state(new_state, token)
    return key_value_result

class _state_expecting_value(_state):
  def __init__(self, parser):
    super(_state_expecting_value, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    key_value_result = None
    if token.type == lexer.COMMENT:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.SPACE:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_EXPECTING_KEY
    elif token.type == lexer.DELIMITER:
      raise RuntimeError('unexpected equal instead of string: %s' % (self.parser.text))
    elif token.type == lexer.DONE:
      key_value_result = key_value(self.parser.key, self.parser.DEFAULT_EMPTY_VALUE)
      new_state = self.parser.STATE_DONE
    elif token.type == lexer.STRING:
      key_value_result = key_value(self.parser.key, token.value)
      new_state = self.parser.STATE_EXPECTING_KEY
    self.change_state(new_state, token)
    return key_value_result
    
class key_value_parser(object):

  DEFAULT_EMPTY_VALUE = None

  KEEP_QUOTES = lexer.KEEP_QUOTES
  ESCAPE_QUOTES = lexer.ESCAPE_QUOTES
  IGNORE_COMMENTS = lexer.IGNORE_COMMENTS

  def __init__(self, options = 0):
    log.add_logging(self, tag = 'key_value_parser')
    self._options = options

    self.STATE_EXPECTING_KEY = _state_expecting_key(self)
    self.STATE_EXPECTING_EQUAL = _state_expecting_equal(self)
    self.STATE_EXPECTING_VALUE = _state_expecting_value(self)
    self.STATE_DONE = _state_done(self)
    self.state = self.STATE_EXPECTING_KEY
    self.key = None
    
  def run(self, text):
    self.log_d('run(%s)' % (text))
    self.text = text

    for token in lexer.tokenize(text, '=', options = self._options):
      key_value = self.state.handle_token(token)
      if key_value:
        self.log_i('parse: new key_value: %s' % (str(key_value)))
        yield key_value
    assert self.state == self.STATE_DONE
      
  @classmethod
  def parse(clazz, text, options = 0):
    return clazz(options = options).run(text)

  @classmethod
  def parse_to_dict(clazz, text, options = 0):
    result = {}
    for kv in clazz.parse(text, options = options):
      result[kv.key] = kv.value
    return result

  def change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state
