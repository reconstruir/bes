#!/usr/bin/env python
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import inspect, os.path as path
from bes.system import compat

class check_type(object):

  @classmethod
  def check(clazz, o, t, name):
    return clazz._check(o, t, name, 2)
  
  @classmethod
  def check_string(clazz, o, name):
    return clazz._check(o, compat.STRING_TYPES, name, 2)

  @classmethod
  def check_string_list(clazz, o, name):
    return clazz._check_homogeneous(o, compat.STRING_TYPES, name, 2)

  @classmethod
  def check_int(clazz, o, name):
    return clazz._check(o, compat.INTEGER_TYPES, name, 2)

  @classmethod
  def check_bool(clazz, o, name):
    return clazz._check(o, bool, name, 2)

  @classmethod
  def check_dict(clazz, o, name):
    return clazz._check(o, dict, name, 2)

  @classmethod
  def check_class(clazz, o, name):
    return clazz._check(o, compat.CLASS_TYPES, name, 2)

  @classmethod
  def _check(clazz, o, t, name, depth, type_blurb = None):
    assert isinstance(name, compat.STRING_TYPES)
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
  def _check_homogeneous(clazz, o, t, name, depth, type_blurb = None):
    try:
      it = enumerate(o)
    except:
      raise TypeError('t should be iterable instead of \"%s\"' % (str(t)))
    for index, item in it:
      clazz._check(item, t, name, depth + 1, type_blurb = type_blurb)

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

  class _check_type_helper(object):
    'Helper class to make check_type.check_foo() methods work.'
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
      check_type._check(obj, self.object_type, name, 2, type_blurb = type_blurb)
    
  class _is_type_helper(object):
    'Helper class to make check_type.is_foo() methods work.'
    def __init__(self, clazz, method_name, object_type):
      self.object_type = object_type
      setattr(clazz, method_name, self)

    def __call__(self, *args, **kwargs):
      assert len(args) == 1
      obj = args[0]
      return isinstance(obj, self.object_type)
    
  class _is_seq_helper(object):
    'Helper class to make check_type.is_foo_list() methods work.'
    def __init__(self, clazz, method_name, object_type):
      self.object_type = object_type
      setattr(clazz, method_name, self)

    def __call__(self, *args, **kwargs):
      assert len(args) == 1
      obj = args[0]
      #return isinstance(obj, self.object_type)
      try:
        for x in iter(obj):
          if not isinstance(x, self.object_type):
            return False
        return True
      except Exception, ex:
        return False
      
  @classmethod
  def register_class(clazz, object_type, name = None, cast_func = None, include_seq = True):
    'Add a check method to check_type for object type with name.'
    clazz.check_class(object_type, 'type')
    name = name or object_type.__name__
    clazz.check_string(name, 'name')

    check_method_name = 'check_%s' % (name)
    if getattr(clazz, check_method_name, None):
      raise RuntimeError('check_type already has a method named \"%s\"' % (check_method_name))
    clazz._check_type_helper(clazz, check_method_name, object_type, cast_func)
    
    is_method_name = 'is_%s' % (name)
    if getattr(clazz, is_method_name, None):
      raise RuntimeError('check_type already has a method named \"%s\"' % (is_method_name))
    clazz._is_type_helper(clazz, is_method_name, object_type)

    if include_seq:
      is_seq_method_name = 'is_%s_seq' % (name)
      if getattr(clazz, is_seq_method_name, None):
        raise RuntimeError('check_type already has a method named \"%s\"' % (is_seq_method_name))
      clazz._is_seq_helper(clazz, is_seq_method_name, object_type)
