#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class btl_function_base(object):

  def __init__(self, state):
    self._state = state

  def make_token(self, *args, **kargs):
    return self._state.make_token(*args, **kargs)
