#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

class bool_util(object):
  'bool util'

  @classmethod
  def parse_bool(clazz, b):
    'Parse a boolean.'
    if isinstance(b, basestring):
      return b.lower() in [ 'true', '1', 't' ]
    elif isinstance(b, bool):
      return b
    elif isinstance(b, int):
      return bool(b)
    else:
      raise TypeError('unknown type for bool conversion: %s - %s' % (str(b), type(b)))
