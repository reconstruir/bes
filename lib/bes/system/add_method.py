#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class _transplanter(object):
   def __init__(self, method, host, method_name = None):
      self.host = host
      self.method = method
      setattr(host, method_name or method.__name__, self)

   def __call__(self, *args, **kwargs):
      nargs = [self.host]
      nargs.extend(args)
      return self.method(*nargs, **kwargs)

def add_method(method, obj, method_name = None):
  'Add a method to an existing object.'
  return _transplanter(method, obj, method_name)
