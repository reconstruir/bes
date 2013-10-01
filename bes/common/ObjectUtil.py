#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json, inspect, new, unittest

class ObjectUtil(object):
  'Object util'

  class Base__(object):
    'Base class for on-the-fly classes.'

    def __str__(self):
      return ObjectUtil.fields_to_string(self)

    def items(self):
      return ObjectUtil.get_fields(self)

    def __repr__(self):
      return json.dumps(self.__dict__)

  @staticmethod
  def get_fields(o):
    'Return a list of only the fields in the object (no functions or methods)'
    try:
      d = o.__dict__
    except:
      d = o
    try:
      fields = d.items()
    except:
      raise RuntimeError('Expecting an object or dict argument.')
    l = [ x for x in fields if not inspect.isfunction(x[1]) ]
    l.sort(lambda x, y: x[0] < y[0])
    return l

  @staticmethod
  def fields_to_string(o, delimiter = ', '):
    'Return a user friendly string for all the fields in an object.'
    return delimiter.join([ '%s=%s' % (x[0], x[1]) for x in ObjectUtil.get_fields(o) if not x[0].startswith('_') ])

  @classmethod
  def set_fields(clazz, o, fields):
    'Set the fields for o.'
    for k, v in fields.items():
      o.__setattr__(k, v)

  @classmethod
  def make(clazz, class_name, fields):
    'Make an object with the given class_name and fields.'
    'A __str__ method is set so that printing the instance is useful.'
    new_clazz = type(class_name, (clazz.Base__,), {})
    instance = new_clazz()
    ObjectUtil.set_fields(instance, fields)
    return instance

  class _transplanter(object):
     def __init__(self, method, host, method_name = None):
        self.host = host
        self.method = method
        setattr(host, method_name or method.__name__, self)

     def __call__(self, *args, **kwargs):
        nargs = [self.host]
        nargs.extend(args)
        return apply(self.method, nargs, kwargs)

  @classmethod
  def add_method(clazz, method, obj, method_name = None):
    'Add a method to an existing object.'
    return ObjectUtil._transplanter(method, obj, method_name)

  @staticmethod
  def listify(o):
    'Turn o into a list if it already is not.'
    if not o:
      return []
    if isinstance(o, list):
      return o
    return [ o ]


class TestObjectUtil(unittest.TestCase):

  def test_x(self):
    pass

if __name__ == "__main__":
  unittest.main()
