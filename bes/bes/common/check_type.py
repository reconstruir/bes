#!/usr/bin/env python
#-*- coding:utf-8 -*-

import inspect

def check_type(o, t, name):

  assert isinstance(name, basestring)
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
  _, filename, line_number, _, _, _ = inspect.stack()[1]
  raise TypeError('\"%s\" should be of type \"%s\" instead of \"%s\" at %s line %d' % (name,
                                                                                   type_blurb,
                                                                                   type(o).__name__,
                                                                                   filename,
                                                                                   line_number))
