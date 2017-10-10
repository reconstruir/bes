#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from .sentence_lexer import sentence_lexer

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_token(self, token):
    raise RuntimeError('unhandled handle_token(%c) in state %s' % (self.name))

  def change_state(self, new_state, token):
    self.parser.change_state(new_state, 'token="%s:%s"'  % (token.token_type, token.value))

  def unexpected_token(self, token):
    raise RuntimeError('unexpected token in %s state: %s' % (self.name, str(token)))

class _state_begin(_state):
  def __init__(self, parser):
    super(_state_begin, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    strings = []
    if token.token_type == sentence_lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.token_type == sentence_lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_BEGIN
    elif token.token_type == sentence_lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
      pass
    elif token.token_type == sentence_lexer.TOKEN_STRING:
      strings = [ token.value ]
      new_state = self.parser.STATE_BEGIN
    else:
      self.unexpected_token(token)
    self.change_state(new_state, token)
    return strings

class _state_name(_state):
  def __init__(self, parser):
    super(_state_name, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    strings = []
    if token.token_type == sentence_lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.token_type == sentence_lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_NAME
    elif token.token_type == sentence_lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
      pass
    elif token.token_type == sentence_lexer.TOKEN_STRING:
      strings = [ token.value ]
      new_state = self.parser.STATE_NAME
    else:
      self.unexpected_token(token)
    self.change_state(new_state, token)
    return strings
  
class _state_value(_state):
  def __init__(self, parser):
    super(_state_value, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    strings = []
    if token.token_type == sentence_lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.token_type == sentence_lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_NAME
    elif token.token_type == sentence_lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
      pass
    elif token.token_type == sentence_lexer.TOKEN_STRING:
      strings = [ token.value ]
      new_state = self.parser.STATE_NAME
    else:
      self.unexpected_token(token)
    self.change_state(new_state, token)
    return strings
  
class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    if token.token_type != sentence_lexer.DONE:
      self.unexpected_token(token)
    self.change_state(self.parser.STATE_DONE, token)
    return []
  
class section_parser(object):

  def __init__(self, log_tag = 'section_parser', options = 0):
    log.add_logging(self, tag = log_tag)

    self.STATE_BEGIN = _state_begin(self)
    self.STATE_DONE = _state_done(self)
    self.STATE_NAME = _state_name(self)
    self.STATE_VALUE = _state_value(self)
    self.state = self.STATE_BEGIN
    
  def run(self, text):
    self.log_d('run(%s)' % (text))
    options = sentence_lexer.KEEP_QUOTES | sentence_lexer.ESCAPE_QUOTES
    for token in sentence_lexer.tokenize(text, log_tag = 'entry_lexer', options = options):
      tokens = self.state.handle_token(token)
      if tokens:
        for s in tokens:
          self.log_i('parse: new token: \"%s\"' % (s))
        yield s
    assert self.state == self.STATE_DONE
      
  def change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state

  @classmethod
  def parse(clazz, text):
    return clazz().run(text)

  @classmethod
  def parse_to_list(clazz, text):
    return [ x for x in clazz.parse(text) ]
