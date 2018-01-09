#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.compat import StringIO
from .string_list_parser import string_list_parser
from bes.common import check, string_util
from .string_lexer import string_lexer_options

class string_list(string_lexer_options.CONSTANTS):

  def __init__(self, values = None):
    self._assign(values)

  def _assign(self, values):
    self._values = []
    for v in values or []:
      check.check_string(v, 'v')
      self._values.append(v)

  def to_string(self, delimiter = ';', quote = False):
    buf = StringIO()
    first = True
    for s in self._values:
      if not first:
        buf.write(delimiter)
      first = False
      if quote:
        s = string_util.quote_if_needed(s)
      buf.write(s)
    return buf.getvalue()
    
  def __str__(self):
    return self.to_string()

  def __eq__(self, other):
    if isinstance(other, string_list):
      return self._values == other._values
    elif isinstance(other, list):
      return self._values == other
    else:
      raise TypeError('other should be of string_list type instead of %s' % (type(other)))

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
  
  def __setitem__(self, i, s):
    check.check_string(s, 's')
    self._values[i] = kv

  def __contains__(self, s):
    return s in self._values
    
  def __add__(self, other):
    check.check_string_list(other, 'other')
    result = string_list()
    for s in self._values:
      result.append(s)
    for s in other:
      result.append(s)
    return result
    
  def extend(self, other):
    check.check_string_list(other, 'other')
    self._values.extend(other)

  def append(self, s):
    check.check_string(s, 's')
    self._values.append(s)

  def remove(self, s):
    check.check_string(s, 's')
    self._values.remove(kv)

  @classmethod
  def parse(clazz, text, options = 0):
    result = string_list()
    for s in string_list_parser.parse(text, options = options):
      result.append(s)
    return result

  def quote(self):
    self._values = [ string_util.quote(s) for s in self._values ]
  
  def unquote(self):
    self._values = [ string_util.unquote(s) for s in self._values ]
  
check.register_class(string_list, include_seq = False)
