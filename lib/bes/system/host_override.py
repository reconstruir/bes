#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from .host import host
from .host_info import host_info
from functools import wraps

class host_override(object):
  'A class with context support for overriding the host info.  Mostly for unit testing.'
  
  def __init__(self, info):
    assert isinstance(info, host_info)
    self._original_info = None
    self._info = info
    
  def __enter__(self):
    self._original_info = host.HOST_INFO
    host.HOST_INFO = self._info
    return self
  
  def __exit__(self, type, value, traceback):
    assert self._original_info != None
    host.HOST_INFO = self._original_info

def host_override_func(info):
  'A decarator to override host.HOST_INFO.'
  def _wrap(func):
    @wraps(func)
    def _caller(self, *args, **kwargs):
      with host_override(info) as over:
        return func(self, *args, **kwargs)
    return _caller
  return _wrap
