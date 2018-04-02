#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect, os.path as path, types
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
    return not clazz.is_string(o) and clazz.is_seq(o, clazz.STRING_TYPES)

  @classmethod
  def is_int(clazz, o):
    return isinstance(o, clazz.INTEGER_TYPES)

  @classmethod
  def is_int_seq(clazz, o):
    return not clazz.is_int(o) and clazz.is_seq(o, clazz.INTEGER_TYPES)
  
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
  def check(clazz, o, t):
    return clazz._check(o, t, 2)
  
  @classmethod
  def check_module(clazz, o):
    return clazz._check(o, types.ModuleType, 2)

  @classmethod
  def check_string(clazz, o):
    return clazz._check(o, clazz.STRING_TYPES, 2)

  @classmethod
  def check_string_seq(clazz, o):
    return clazz._check_seq(o, clazz.STRING_TYPES, 2)

  @classmethod
  def check_tuple_seq(clazz, o):
    return clazz._check_seq(o, tuple, 2)

  @classmethod
  def check_int(clazz, o):
    return clazz._check(o, clazz.INTEGER_TYPES, 2)

  @classmethod
  def check_bool(clazz, o):
    return clazz._check(o, bool, 2)

  @classmethod
  def check_tuple(clazz, o):
    return clazz._check(o, tuple, 2)

  @classmethod
  def check_dict(clazz, o, key_type = None, value_type = None):
    o = clazz._check(o, dict, 2)
    if key_type or value_type:
      for key, value in o.items():
        if key_type:
          clazz._check(key, key_type, 2)
        if value_type:
          clazz._check(value, value_type, 2)
    return o
  
  @classmethod
  def check_set(clazz, o, entry_type = None):
    o = clazz._check(o, set, 2)
    if entry_type:
      clazz._check_seq(o, entry_type, 2)
    return o

  @classmethod
  def check_list(clazz, o, entry_type = None):
    o = clazz._check(o, list, 2)
    if entry_type:
      clazz._check_seq(o, entry_type, 2)
    return o

  @classmethod
  def check_class(clazz, o):
    return clazz._check(o, clazz.CLASS_TYPES, 2)

  @classmethod
  def _check(clazz, o, t, depth, type_blurb = None):
    if isinstance(o, t):
      return o
    type_blurb = type_blurb or clazz._make_type_blurb(t)
    if not type_blurb:
      raise TypeError('t should be a type or tuple of types instead of \"%s\"' % (str(t)))
    _, filename, line_number, _, _, _ = inspect.stack()[depth]
    name = clazz._previous_frame_object_name(o, depth)
    raise TypeError('\"%s\" should be of type \"%s\" instead of \"%s\" at %s line %d' % (name,
                                                                                         type_blurb,
                                                                                         type(o).__name__,
                                                                                         path.abspath(filename),
                                                                                         line_number))
  @classmethod
  def check_seq(clazz, o, t):
    return clazz._check_seq(o, t, 2)

  @classmethod
  def _check_seq(clazz, o, t, depth, type_blurb = None):
    try:
      it = enumerate(o)
    except:
      raise TypeError('t should be iterable instead of \"%s\"' % (str(t)))
    for index, entry in it:
      clazz._check(entry, t, depth + 1, type_blurb = type_blurb)
    return o

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
      assert len(args) == 1
      obj = args[0]
      if not isinstance(obj, self.object_type) and self.cast_func:
        obj = self.cast_func(self.object_type, obj)
      type_blurb = kwargs.get('type_blurb', None)
      return check._check(obj, self.object_type, 2, type_blurb = type_blurb)
    
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
      assert len(args) == 1
      obj = args[0]
      return check._check_seq(obj, self.object_type, 2, type_blurb = None)
    
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
    clazz.check_class(object_type)
    name = name or object_type.__name__
    clazz.check_string(name)
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

  @classmethod
  def _previous_frame_object_name(clazz, obj, depth):
    'Return the name for obj in the previous frame.'
    frame = clazz._crawl_frames(depth + 1)
    for k, v in frame.f_locals.items():
      if id(v) == id(obj):
        return k
    return '<unknown>'
      
  @classmethod
  def _crawl_frames(clazz, depth):
    'Return the name for obj in the previous frame.'
    frame = inspect.currentframe()
    for i in range(0, depth + 1):
      frame = frame.f_back
    return frame
