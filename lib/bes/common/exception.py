#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from functools import wraps

def ignore_exception(exception_result):
  'Ignore exceptions.  If any are caught, return exception_result.'
  def _wrap(func):
    @wraps(func)
    def _caller(self, *args, **kwargs):
      try:
        return func(self, *args, **kwargs)
      except:
        return exception_result
    return _caller
  return _wrap
