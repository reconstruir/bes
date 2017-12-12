#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
from bes.compat import StringIO
from .key_value_parser import key_value_parser
from .key_value import key_value
from bes.common import check_type, object_util
from bes.text import string_lexer_options

class key_value_list(string_lexer_options.CONSTANTS):

  def __init__(self, values = None):
    self._assign(values)

  def _assign(self, values):
    self._values = []
    for v in values or []:
      if not isinstance(v, key_value):
        v = key_value(*v)
      self._values.append(v)

  def to_string(self, delimiter = '=', value_delimiter = ';', quote = False):
    buf = StringIO()
    first = True
    for kv in iter(self):
      if not first:
        buf.write(value_delimiter)
      first = False
      buf.write(kv.to_string(delimiter = delimiter, quote_value = quote))
    return buf.getvalue()
    
  def __str__(self):
    return self.to_string()

  def __eq__(self, other):
    if isinstance(other, key_value_list):
      return self._values == other._values
    elif isinstance(other, list):
      return self._values == other
    else:
      raise TypeError('other should be of key_value_list type instead of %s' % (type(other)))

  def __ne__(self, other):
    return self._values != other._values

  def __lt__(self, other):
    return self._values < other._values

  def __le__(self, other):
    return self._values <= other._values

  def __gt__(self, other):
    return self._values > other._values

  def __ge__(self, other):
    return self._values >= other._values
    
  def __len__(self):
    return len(self._values)

  def __iter__(self):
    return iter(self._values)

  def __getitem__(self, i):
    return self._values[i]
  
  def __setitem__(self, i, kv):
    if not isinstance(kv, key_value):
      raise TypeError('kv should be of key_value type instead of %s' % (type(kv)))
    self._values[i] = kv

  def __contains__(self, what):
    if isinstance(what, key_value):
      return what in self._values
    for kv in self._values:
      if kv.key == what:
        return True
    return False
    
  def __add__(self, other):
    if not isinstance(other, key_value_list):
      raise TypeError('other should be of key_value_list type instead of %s' % (type(other)))
    result = key_value_list()
    result._values = copy.deepcopy(self._values)
    result._values.extend(copy.deepcopy(other._values))
    return result
    
  def extend(self, other):
    if not isinstance(other, key_value_list):
      raise TypeError('other should be of key_value_list type instead of %s' % (type(other)))
    self._values.extend(other)

  def append(self, kv):
    if not isinstance(kv, key_value):
      raise TypeError('kv should be of key_value type instead of %s' % (type(kv)))
    self._values.append(kv)

  def remove(self, kv):
    if not isinstance(kv, key_value):
      raise TypeError('kv should be of key_value type instead of %s' % (type(kv)))
    self._values.remove(kv)

  def find_key_value(self, kv):
    if not isinstance(kv, key_value):
      raise TypeError('kv should be of key_value type instead of %s' % (type(kv)))
    for next_kv in self._values:
      if next_kv == kv:
        return next_kv
    return None

  def find_key(self, key):
    for next_kv in self._values:
      if next_kv.key == key:
        return next_kv
    return None

  def find_all_key(self, key):
    result = []
    for next_kv in self._values:
      if next_kv.key == key:
        result.append(next_kv)
    return result

  def remove_key(self, key):
    self._values = [ kv for kv in self._values if kv.key != key ]

  @classmethod
  def parse(clazz, text, options = 0):
    result = clazz()
    for kv in key_value_parser.parse(text, options = options):
      result.append(kv)
    return result

  def is_homogeneous(self, key_type, value_type):
    'Return True if all items in d are of the given key_type and value_type.'
    for kv in self._values:
      if not kv.is_instance(key_type, value_type):
        return False
    return True

  @classmethod
  def is_key_value_list(clazz, o):
    'Return True if o is either a key_value_list or a python iterable of key_values.'
    if isinstance(o, key_value_list):
      return True
    return isinstance(o, (list, tuple)) and object_util.is_homogeneous(o, key_value)

  @classmethod
  def verify_key_value_list(clazz, o):
    if isinstance(o, key_value_list):
      return o
    if not object_util.is_homogeneous(o, key_value):
      return None
    return clazz([ v for v in o ])

  def to_dict(self):
    result = {}
    for next_kv in self._values:
      result[next_kv.key] = next_kv.value
    return result
check_type.register_class(key_value_list, include_seq = False)

