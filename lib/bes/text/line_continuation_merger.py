#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import log
from .text_line import text_line

class _state(object):

  def __init__(self, parser):
    self.name = self.__class__.__name__[1:]
    log.add_logging(self, tag = '%s.%s' % (parser.__class__.__name__, self.name))
    self.parser = parser
  
  def handle_token(self, token):
    raise RuntimeError('unhandled handle_token(%s) in state %s' % (token, self.name))

  def change_state(self, new_state, token):
    self.parser._change_state(new_state, 'token="%s"'  % (str(token)))

  def unexpected_token(self, token):
    raise RuntimeError('unexpected token in %s state: %s' % (token, self.name))

class _state_expecting_line(_state):
  def __init__(self, parser):
    super(_state_expecting_line, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    if token is None:
      new_state = self.parser.STATE_DONE
    elif token.has_continuation:
      new_state = self.parser.STATE_CONTINUATION
      assert not self.parser._buffer
      self.parser._buffer = [ token ]
      assert not self.parser._blank_buffer
      self.parser._blank_buffer = [ text_line(token.line_number + 1, '') ]
    else:
      new_state = self.parser.STATE_EXPECTING_LINE
      yield [ token ]
    self.change_state(new_state, token)
    
class _state_continuation(_state):
  def __init__(self, parser):
    super(_state_continuation, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    new_state = None
    assert self.parser._buffer
    self.parser._buffer.append(token)
    if token is None:
      raise RuntimeError('Unexpected end of tokens expecting a continuation in state %s' % (self.name))
    elif token.has_continuation:
      new_state = self.parser.STATE_CONTINUATION
      self.parser._blank_buffer.append(text_line(token.line_number + 1, ''))
    else:
      new_state = self.parser.STATE_EXPECTING_LINE
      yield self.parser._buffer
      for blank_line in self.parser._blank_buffer:
        yield [ blank_line ]
      self.parser._buffer = None
      self.parser._blank_buffer = None
    self.change_state(new_state, token)
    
class _state_done(_state):
  def __init__(self, parser):
    super(_state_done, self).__init__(parser)

  def handle_token(self, token):
    self.log_d('handle_token(%s)' % (str(token)))
    raise RuntimeError('Unexpected token(%s) in state %s' % (token, self.name))
    return []
  
class line_continuation_merger(object):

  def __init__(self):
    log.add_logging(self, tag = 'line_continuation_merger')

    self.STATE_CONTINUATION = _state_continuation(self)
    self.STATE_DONE = _state_done(self)
    self.STATE_EXPECTING_LINE = _state_expecting_line(self)
    self.state = self.STATE_EXPECTING_LINE
    self._buffer = None
    self._blank_buffer = None
    
  def _run(self, tokens):
    self.log_d('_run(%s)' % (tokens))

    for token in [ t for t in tokens ] + [ None ]:
      for result in self.state.handle_token(token):
        if len(result) == 1:
          line = result[0]
          self.log_i('parse: new untouched line: \"%s\"' % (str(line)))
          yield line
        else:
          merged_line = text_line.merge(result)
          self.log_i('parse: new merged line: \"%s\"' % (str(merged_line)))
          yield merged_line
    assert self.state == self.STATE_DONE
      
  def _change_state(self, new_state, msg):
    assert new_state
    if new_state != self.state:
      self.log_d('transition: %20s -> %-20s; %s'  % (self.state.__class__.__name__, new_state.__class__.__name__, msg))
      self.state = new_state

  @classmethod
  def merge(clazz, tokens):
    'Merge a sequence of text_line objects. Yield a sequence with line'
    'continuations merged into one.  The resulting empty lines are kept with'
    'empty text.'
    return clazz()._run(tokens)

  @classmethod
  def merge_to_list(clazz, tokens):
    return [ x for x in clazz.merge(tokens) ]
