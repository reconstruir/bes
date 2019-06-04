#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.compat import compat
from .string_util import string_util

class bool_util(object):
  'bool util'

  @classmethod
  def parse_bool(clazz, b):
    'Parse a boolean.'
    if string_util.is_string(b):
      return b.lower() in [ 'true', '1', 't' ]
    elif isinstance(b, bool):
      return b
    elif isinstance(b, compat.INTEGER_TYPES):
      return bool(b)
    else:
      raise TypeError('unknown type for bool conversion: %s - %s' % (str(b), type(b)))
