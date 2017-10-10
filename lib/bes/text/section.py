#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from .sentence_lexer import sentence_lexer

class section(object):

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
