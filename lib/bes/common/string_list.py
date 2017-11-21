#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system import compat
from bes.compat import StringIO
from .object_util import object_util
from .string_util import string_util

class string_list(object):
  'string list helpers'

  @classmethod
  def remove_if(clazz, l, blacklist):
    'Remove any items in l that are present both in l and blacklist preserving order.'
    blacklist_set = set(blacklist)
    result = []
    for x in l:
      if x not in blacklist_set:
        result.append(x)
    return result

  @classmethod
  def is_string_list(clazz, l):
    'Return True if l is a homogenous string list.'
    return object_util.is_homogeneous(l, compat.STRING_TYPES)

  @classmethod
  def to_string(clazz, l, delimiter = ';', quote = False):
    buf = StringIO()
    first = True
    for s in iter(l):
      if not compat.is_string(s):
        raise TypeError('not a string: %s - %s' % (str(s), type(s)))
      if not first:
        buf.write(delimiter)
      first = False
      if quote:
        s = string_util.quote_if_needed(s)
      buf.write(s)
    return buf.getvalue()
