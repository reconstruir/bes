#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from bes.compat.StringIO import StringIO
from ..system.check import check
from bes.common.string_util import string_util

class key_value(namedtuple('key_value', 'key,value')):

  def __new__(clazz, key, value):
    return clazz.__bases__[0].__new__(clazz, key, value)

  def __str__(self):
    return self.to_string()

  def to_string(self, delimiter = '=', quote_value = False):
    buf = StringIO()
    buf.write(str(self.key))
    buf.write(delimiter)
    value = str(self.value)
    if quote_value:
      value = string_util.quote_if_needed(value)
    buf.write(value)
    return buf.getvalue()

  def is_instance(self, key_type, value_type):
    'Return True if the key and value types are instance of the key_type and value_type.'
    if not isinstance(self.key, key_type):
      return False
    if not isinstance(self.value, value_type):
      return False
    return True

  @classmethod
  def parse(clazz, text, delimiter = '='):
    key, actual_delimiter, value = text.partition(delimiter)
    if actual_delimiter != delimiter:
      raise ValueError('invalid key value: \"%s\"' % (text))
    return clazz(key.strip(), value.strip())

check.register_class(key_value, include_seq = False)
