#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple, OrderedDict
from io import StringIO

class key_value(namedtuple('key_value', 'key,value')):

  def __new__(clazz, key, value):
    return clazz.__bases__[0].__new__(clazz, key, value)

  def __str__(self):
    return self.to_string()

  def to_string(self, delimiter = '='):
    buf = StringIO()
    buf.write(unicode(self.key))
    buf.write(unicode(delimiter))
    buf.write(unicode(self.value))
    return buf.getvalue()

  def is_instance(self, key_type, value_type):
    'Return True if the key and value types are instance of the key_type and value_type.'
    if not isinstance(self.key, key_type):
      return False
    if not isinstance(self.value, value_type):
      return False
    return True
