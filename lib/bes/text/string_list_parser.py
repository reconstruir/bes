#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.log import log
from .string_lexer import string_lexer, string_lexer_options

class string_list_parser(string_lexer_options.CONSTANTS):

  def __init__(self, options = 0):
    log.add_logging(self, tag = 'string_list_parser')

    self._options = options
    self.STATE_EXPECTING_STRING = _state_expecting_string(self)
    self.STATE_DONE = _state_done(self)
    self.state = self.STATE_EXPECTING_STRING

  def _run(self, text):
    self.log_d('_run(%s)' % (text))

    for token in string_lexer.tokenize(text, 'string_list_parser', options = self._options):
      strings = self.state.handle_token(token)
      if strings:
        for s in strings:
          self.log_i('parse: new string: \"%s\"' % (s))
        yield s
    assert self.state == self.STATE_DONE
      
  def _change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state

  @classmethod
  def parse(clazz, text, options = 0):
    return clazz(options = options)._run(text)

  @classmethod
  def parse_to_list(clazz, text, options = 0):
    return [ x for x in clazz.parse(text, options = options) ]

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_token(self, token):
    raise RuntimeError('unhandled handle_token(%c) in state %s' % (self.name))

  def change_state(self, new_state, token):
    self.parser._change_state(new_state, 'token="%s:%s"'  % (token.token_type, token.value))

  def unexpected_token(self, token):
    raise RuntimeError('unexpected token in %s state: %s' % (self.name, str(token)))

class _state_expecting_string(_state):
  def __init__(self, parser):
    super(_state_expecting_string, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    strings = []
    if token.token_type == string_lexer.TOKEN_COMMENT:
      new_state = self.parser.STATE_DONE
    elif token.token_type == string_lexer.TOKEN_SPACE:
      new_state = self.parser.STATE_EXPECTING_STRING
    elif token.token_type == string_lexer.TOKEN_DONE:
      new_state = self.parser.STATE_DONE
      pass
    elif token.token_type == string_lexer.TOKEN_STRING:
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
    if token.token_type != string_lexer.TOKEN_DONE:
      self.unexpected_token(token)
    self.change_state(self.parser.STATE_DONE, token)
    return []
  
