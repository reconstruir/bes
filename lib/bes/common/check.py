#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect, os.path as path
from bes.system import compat

class check(object):

  STRING_TYPES = compat.STRING_TYPES
  INTEGER_TYPES = compat.INTEGER_TYPES
  CLASS_TYPES = compat.CLASS_TYPES
  
  @classmethod
  def is_string(clazz, o):
    return isinstance(o, clazz.STRING_TYPES)

  @classmethod
  def is_string_seq(clazz, o):
    return clazz.is_seq(o, clazz.STRING_TYPES)

  @classmethod
  def is_int(clazz, o):
    return isinstance(o, clazz.INTEGER_TYPES)

  @classmethod
  def is_bool(clazz, o):
    return isinstance(o, bool)

  @classmethod
  def is_dict(clazz, o):
    return isinstance(o, dict)

  @classmethod
  def is_set(clazz, o):
    return isinstance(o, set)

  @classmethod
  def is_class(clazz, o):
    return isinstance(o, clazz.CLASS_TYPES)

  @classmethod
  def is_seq(clazz, o, t):
    'Return True if l is iterable and all its entries are of a given type.'
    try:
      for x in iter(o):
        if not isinstance(x, t):
          return False
      return True
    except:
      return False
  
  @classmethod
  def check(clazz, o, t, name):
    clazz._check(o, t, name, 2)
  
  @classmethod
  def check_string(clazz, o, name):
    clazz._check(o, clazz.STRING_TYPES, name, 2)

  @classmethod
  def check_string_seq(clazz, o, name):
    clazz._check_seq(o, clazz.STRING_TYPES, name, 2)

  @classmethod
  def check_int(clazz, o, name):
    clazz._check(o, clazz.INTEGER_TYPES, name, 2)

  @classmethod
  def check_bool(clazz, o, name):
    clazz._check(o, bool, name, 2)

  @classmethod
  def check_dict(clazz, o, name, key_type = None, value_type = None):
    clazz._check(o, dict, name, 2)
    if key_type or value_type:
      for key, value in o.items():
        if key_type:
          clazz._check(key, key_type, name + '-key', 2)
        if value_type:
          clazz._check(value, value_type, name + '-value', 2)

  @classmethod
  def check_set(clazz, o, name, entry_type = None):
    clazz._check(o, set, name, 2)
    if entry_type:
      clazz._check_seq(o, entry_type, name + '-entry', 2)

  @classmethod
  def check_list(clazz, o, name, entry_type = None):
    clazz._check(o, list, name, 2)
    if entry_type:
      clazz._check_seq(o, entry_type, name + '-entry', 2)

  @classmethod
  def check_class(clazz, o, name):
    clazz._check(o, clazz.CLASS_TYPES, name, 2)

  @classmethod
  def _check(clazz, o, t, name, depth, type_blurb = None):
    assert isinstance(name, clazz.STRING_TYPES)
    if isinstance(o, t):
      return o
    type_blurb = type_blurb or clazz._make_type_blurb(t)
    if not type_blurb:
      raise TypeError('t should be a type or tuple of types instead of \"%s\"' % (str(t)))
    _, filename, line_number, _, _, _ = inspect.stack()[depth]
    raise TypeError('\"%s\" should be of type \"%s\" instead of \"%s\" at %s line %d' % (name,
                                                                                         type_blurb,
                                                                                         type(o).__name__,
                                                                                         path.abspath(filename),
                                                                                         line_number))
  @classmethod
  def check_seq(clazz, o, t, name):
    clazz._check_seq(o, t, name, 2)

  @classmethod
  def _check_seq(clazz, o, t, name, depth, type_blurb = None):
    try:
      it = enumerate(o)
    except:
      raise TypeError('t should be iterable instead of \"%s\"' % (str(t)))
    for index, entry in it:
      clazz._check(entry, t, name, depth + 1, type_blurb = type_blurb)

  @classmethod
  def _make_type_blurb(clazz, t):
    if isinstance(t, type):
      return t.__name__
    elif isinstance(t, (tuple, list)):
      names = [ i.__name__ for i in t ]
      if len(names) == 1:
        type_blurb = names[0]
      else:
        last = names.pop(-1)
        type_blurb = ', '.join(names) + ' or ' + last
      return type_blurb
    return None

  class _check_helper(object):
    'Helper class to make check.check_foo() methods work.'
    def __init__(self, clazz, method_name, object_type, cast_func):
      self.object_type = object_type
      self.cast_func = cast_func
      setattr(clazz, method_name, self)

    def __call__(self, *args, **kwargs):
      assert len(args) == 2
      obj = args[0]
      if self.cast_func:
        obj = self.cast_func(self.object_type, obj)
      name = args[1]
      type_blurb = kwargs.get('type_blurb', None)
      check._check(obj, self.object_type, name, 2, type_blurb = type_blurb)
    
  class _is_type_helper(object):
    'Helper class to make check.is_foo() methods work.'
    def __init__(self, clazz, method_name, object_type):
      self.object_type = object_type
      setattr(clazz, method_name, self)

    def __call__(self, *args, **kwargs):
      assert len(args) == 1
      obj = args[0]
      return isinstance(obj, self.object_type)
    
  class _check_seq_helper(object):
    'Helper class to make check.check_foo_seq() methods work.'
    def __init__(self, clazz, method_name, object_type):
      self.object_type = object_type
      setattr(clazz, method_name, self)

    def __call__(self, *args, **kwargs):
      assert len(args) == 2
      obj = args[0]
      name = args[1]
      return check._check_seq(obj, self.object_type, name, 2, type_blurb = None)
    
  class _is_seq_helper(object):
    'Helper class to make check.is_foo_seq() methods work.'
    def __init__(self, clazz, method_name, object_type):
      self.object_type = object_type
      setattr(clazz, method_name, self)

    def __call__(self, *args, **kwargs):
      assert len(args) == 1
      obj = args[0]
      return check.is_seq(obj, self.object_type)
      
  @classmethod
  def register_class(clazz, object_type, name = None, cast_func = None, include_seq = True):
    'Add a check method to check for object type with name.'
    clazz.check_class(object_type, 'type')
    name = name or object_type.__name__
    clazz.check_string(name, 'name')

    check_method_name = 'check_%s' % (name)
    if getattr(clazz, check_method_name, None):
      raise RuntimeError('check already has a method named \"%s\"' % (check_method_name))
    clazz._check_helper(clazz, check_method_name, object_type, cast_func)
    
    is_method_name = 'is_%s' % (name)
    if getattr(clazz, is_method_name, None):
      raise RuntimeError('check already has a method named \"%s\"' % (is_method_name))
    clazz._is_type_helper(clazz, is_method_name, object_type)

    if include_seq:
      is_seq_method_name = 'is_%s_seq' % (name)
      if getattr(clazz, is_seq_method_name, None):
        raise RuntimeError('check already has a method named \"%s\"' % (is_seq_method_name))
      clazz._is_seq_helper(clazz, is_seq_method_name, object_type)

      check_seq_method_name = 'check_%s_seq' % (name)
      if getattr(clazz, check_seq_method_name, None):
        raise RuntimeError('check already has a method named \"%s\"' % (check_seq_method_name))
      clazz._check_seq_helper(clazz, check_seq_method_name, object_type)
      
