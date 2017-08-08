#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from string_lexer import string_lexer, string_lexer_options

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_token(self, token):
    raise RuntimeError('unhandled handle_token(%c) in state %s' % (self.name))

  def change_state(self, new_state, token):
    self.parser.change_state(new_state, 'token="%s:%s"'  % (token.type, token.value))

  def unexpected_token(self, token):
    raise RuntimeError('unexpected token in %s state: %s' % (self.name, str(token)))

class _state_expecting_string(_state):
  def __init__(self, parser):
    super(_state_expecting_string, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    strings = []
    if token.type == string_lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.type == string_lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_STRING
    elif token.type == string_lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
      pass
    elif token.type == string_lexer.TOKEN_STRING:
      strings = [ token.value ]
      new_state = self.parser.STATE_EXPECTING_STRING
    else:
      self.unexpected_token(token)
    self.change_state(new_state, token)
    return strings
    
class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    if token.type != string_lexer.DONE:
      self.unexpected_token(token)
    self.change_state(self.parser.STATE_DONE, token)
    return []
  
class string_list_parser(string_lexer_options):

  def __init__(self, options = 0):
    log.add_logging(self, tag = 'string_list_parser')

    self._options = options
    self.STATE_EXPECTING_STRING = _state_expecting_string(self)
    self.STATE_DONE = _state_done(self)
    self.state = self.STATE_EXPECTING_STRING
    
  def run(self, text):
    self.log_d('run(%s)' % (text))

    for token in string_lexer.tokenize(text, 'string_list_parser', options = self._options):
      strings = self.state.handle_token(token)
      if strings:
        for s in strings:
          self.log_i('parse: new string: \"%s\"' % (s))
        yield s
    assert self.state == self.STATE_DONE
      
  @classmethod
  def parse(clazz, text, options = 0):
    return clazz(options = options).run(text)

  def change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state
