#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import itertools
from bes.compat.StringIO import StringIO
from bes.compat.cmp import cmp
from bes.compat.zip import zip
from bes.common.algorithm import algorithm
from bes.common.check import check

class type_checked_list(object):

  def __init__(self, values = None):
    self._value_type = self.value_type()
    self._assign(values)

  @classmethod
  def cast_value(clazz, value):
    return value

  @classmethod
  def value_type(clazz):
    value_type = getattr(clazz, '__value_type__', None)
    if not value_type:
      raise TypeError('No __value_type__ attribute found in %s' % (str(clazz)))
    check.check(value_type, ( type, tuple ))
    return value_type
  
  def __repr__(self):
    return repr(self._values)
    
  def _assign(self, values):
    self._values = []
    for v in values or []:
      v = self.cast_value(v)
      check.check(v, self._value_type)
      self._values.append(v)

  def compare(self, other):
    check.check(other, ( type_checked_list, list, tuple ))
    len_cmp = cmp(len(self), len(other))
    if len_cmp != 0:
      return len_cmp
    other_values = self._get_values(other)
    for a, b in zip(self._values, other_values):
      next_cmp = cmp(a, b)
      if next_cmp != 0:
        return next_cmp
    return 0

  @classmethod
  def _get_values(clazz, obj):
    if isinstance(obj, type_checked_list):
      return obj._values
    else:
      check.check(obj, ( list, tuple ))
      return obj
  
  def __eq__(self, other):
    return self.compare(other) == 0

  def __ne__(self, other):
    return self.compare(other) != 0

  def __lt__(self, other):
    return self.compare(other) < 0

  def __le__(self, other):
    return self.compare(other) <= 0

  def __gt__(self, other):
    return self.compare(other) > 0

  def __ge__(self, other):
    return self.compare(other) >= 0
    
  def __len__(self):
    return len(self._values)

  def __iter__(self):
    return iter(self._values)

  def __getitem__(self, i):
    if isinstance(i, slice):
      return self.__class__(self._values[i])
    return self._values[i]
  
  def __setitem__(self, i, v):
    check.check(v, self._value_type)
    self._values[i] = v

  def __contains__(self, v):
    return v in self._values
    
  def __add__(self, other):
    check.check(other, ( type_checked_list, list, tuple ))
    result = self.__class__()
    for s in self._values:
      result.append(s)
    for s in self._get_values(other):
      result.append(s)
    return result
    
  def extend(self, other):
    check.check(other, ( type_checked_list, list, tuple ))
    self._values.extend(self._get_values(other))

  def append(self, v):
    check.check(v, self._value_type)
    self._values.append(v)

  def remove(self, v):
    check.check(v, self._value_type)
    self._values.remove(v)

  def remove_dups(self):
    self._values = algorithm.unique(self._values)

  def to_list(self):
    return self._values[:]
  
  def to_set(self):
    result = set()
    for s in self._values:
      result.add(s)
    return result

  def sort(self, key = None, reverse = False):
    self._values = sorted(self._values, key = key, reverse = reverse)

  def to_string(self, delimiter = ' '):
    buf = StringIO()
    first = True
    for item in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(item))
    return buf.getvalue()
