#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect
from bes.system import compat

class check_type(object):

  @classmethod
  def check(clazz, o, t, name):
    return clazz._check(o, t, name, 2)
  
  @classmethod
  def check_string(clazz, o, name):
    return clazz._check(o, compat.STRING_TYPES, name, 2)

  @classmethod
  def check_int(clazz, o, name):
    return clazz._check(o, compat.INTEGER_TYPES, name, 2)

  @classmethod
  def check_bool(clazz, o, name):
    return clazz._check(o, bool, name, 2)

  @classmethod
  def check_dict(clazz, o, name):
    return clazz._check(o, dict, name, 2)

  @classmethod
  def check_class(clazz, o, name):
    return clazz._check(o, compat.CLASS_TYPES, name, 2)

  @classmethod
  def _check(clazz, o, t, name, depth):
    assert isinstance(name, compat.STRING_TYPES)
    success = isinstance(o, t)
    if success:
      return o
    if isinstance(t, type):
      type_blurb = t.__name__
    elif isinstance(t, tuple):
      names = [ i.__name__ for i in t ]
      last = names.pop(-1)
      type_blurb = ', '.join(names) + ' or ' + last
    else:
      raise TypeError('t should be a type or tuple of types instead of \"%s\"' % (str(t)))
    _, filename, line_number, _, _, _ = inspect.stack()[depth]
    raise TypeError('\"%s\" should be of type \"%s\" instead of \"%s\" at %s line %d' % (name,
                                                                                         type_blurb,
                                                                                         type(o).__name__,
                                                                                         filename,
                                                                                         line_number))
  

