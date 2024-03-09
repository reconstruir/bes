#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import itertools
import random

from bes.compat.StringIO import StringIO
from bes.compat.cmp import cmp
from bes.compat.zip import zip
from bes.common.algorithm import algorithm
from ..system.check import check

from ..property.cached_class_property import cached_class_property

class type_checked_list(object):

  def __init__(self, values = None):
    self._assign(values)

  def __repr__(self):
    return repr(self._values)
    
  @classmethod
  def cast_value(clazz, value):
    return value

  @cached_class_property
  def value_type(clazz):
    value_type = getattr(clazz, '__value_type__', None)
    if not value_type:
      raise TypeError('No __value_type__ attribute found in %s' % (str(clazz)))
    check.check(value_type, ( type, tuple ))
    return value_type

  @cached_class_property
  def _check_value_method(clazz):
    value_type_name = getattr(clazz.value_type, '__name__', None)
    if not value_type_name:
      return None
    check_method_name = f'check_{value_type_name}'
    return getattr(check, check_method_name, None)

  @classmethod
  def _check_value(clazz, v):
    check_method = clazz._check_value_method
    if check_method:
      v = check_method(v)
    else:
      v = clazz.cast_value(v)
      v = check.check(v, clazz.value_type)
    return v

  @cached_class_property
  def _check_list_method(clazz):
    list_type_name = getattr(clazz, '__name__', None)
    if not list_type_name:
      return None
    check_method_name = f'check_{list_type_name}'
    return getattr(check, check_method_name, None)

  @classmethod
  def _check_list(clazz, l):
    check_method = clazz._check_list_method
    if check_method:
      l = check_method(l)
    else:
      l = check.check(l, clazz)
    return l
  
  def _assign(self, values):
    self._values = []
    for v in values or []:
      v = self._check_value(v)
      self._values.append(v)

  def compare(self, other):
    check.check(other, ( type_checked_list, list, tuple ), allow_none = True)

    if other == None:
      return -1
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
    if other == None:
      return False
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
    check.check(i, ( int, slice ))
    
    if isinstance(i, slice):
      return self.__class__(self._values[i])
    return self._values[i]
  
  def __setitem__(self, i, v):
    check.check(i, ( int, slice ))

    if isinstance(i, slice):
      v = self._check_list(v)
    else:
      assert isinstance(i, int)
      v = self._check_value(v)
    self._values[i] = v

  def __contains__(self, v):
    return v in self._values
    
  def __add__(self, other):
    result = self.__class__()
    result.extend(self)
    result.extend(other)
    return result
    
  def extend(self, other):
    if isinstance(other, self.__class__):
      self._values.extend(other._values)
    elif check.is_seq(other):
      for v in other:
        v = self._check_value(v)
        self._values.append(v)
    else:
      raise TypeError(f'Unknown type for other: {type(other)} - "{other}"')
    
  def append(self, v):
    v = self._check_value(v)

    self._values.append(v)

  def remove(self, v):
    v = self._check_value(v)

    self._values.remove(v)

  def remove_dups(self):
    self._values = algorithm.unique(self._values)

  def remove_in_set(self, s):
    check.check_set(s, self.value_type)

    self._values = [ item for item in self._values if item not in s ]

  def remove_by_callable(self, callable_):
    check.check_callable(callable_)

    self._values = [ item for item in self._values if not callable_(item) ]

  def keep_by_callable(self, callable_):
    check.check_callable(callable_)

    self._values = [ item for item in self._values if callable_(item) ]
    
  def to_list(self):
    return self._values[:]
  
  def to_set(self):
    result = set()
    for s in self._values:
      result.add(s)
    return result

  def sort(self, key = None, reverse = False):
    self._values = sorted(self._values, key = key, reverse = reverse)

  def sorted_(self, key = None, reverse = False):
    return self.__class__(sorted(self._values, key = key, reverse = reverse))
    
  def to_string(self, delimiter = ' '):
    buf = StringIO()
    first = True
    for item in iter(self):
      if not first:
        buf.write(delimiter)
      first = False
      buf.write(str(item))
    return buf.getvalue()

  def pop(self, index = -1):
    return self._values.pop(index)

  @classmethod
  def check_cast_func(clazz, obj):
    if isinstance(obj, clazz):
      return obj
    if check.is_seq(obj):
      return clazz([ x for x in obj ])
    return obj

  def shuffle(self):
    random.shuffle(self._values)
    
  def shuffled(self):
    values = self._values[:]
    random.shuffle(values)
    return self.__class__(values)

  @classmethod
  def register_check_class(clazz):
    check.register_class(clazz,
                         include_seq = False,
                         cast_func = clazz.check_cast_func)

  def prepend(self, value):
    value = self._check_value(value)

    self._values.insert(0, value)

  def insert(self, index, value):
    check.check_int(index)
    value = self._check_value(value)

    if index < 0:
      index = len(self._values) + index + 1    
    
    self._values.insert(index, value)
    return index

  def insert_values(self, index, values):
    check.check_int(index)
    values = self._check_list(values)

    top, bottom = self.partition_for_insert(index)
    self._values = top + values + bottom
    return index

  def partition_for_insert(self, index):
    check.check_int(index)

    if index < 0:
      index = len(self._values) + index + 1    
    
    top = self[0:index]
    bottom = self[index:]
    return top, bottom
  
  def clear(self):
    self._values = []

  def remove_by_index(self, index):
    check.check_int(index)
    
    removed_value = self._values.pop(index)
    return removed_value
    
  def replace_by_index(self, index, value):
    check.check_int(index)
    v = self._check_value(value)
    
    old_value = self._values[index]
    self._values[index] = value
    return old_value
