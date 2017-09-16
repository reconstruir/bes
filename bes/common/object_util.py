#!/usr/bin/env python
#-*- coding:utf-8 -*-

import json, inspect, new
from itertools import chain

class object_util(object):
  'Object util'

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
    return delimiter.join([ '%s=%s' % (x[0], x[1]) for x in object_util.get_fields(o) if not x[0].startswith('_') ])

  @classmethod
  def set_fields(clazz, o, fields):
    'Set the fields for o.'
    for k, v in fields.items():
      o.__setattr__(k, v)

  @classmethod
  def is_iterable(clazz, o):
    'Return True if o is iterable.'
    try:
      return o.__iter__
    except:
      return False
    
  @classmethod
  def listify(clazz, o):
    'Return a list version of o whether its iterable or not.'
    if isinstance(o, list): #clazz.is_iterable(o):
      return [ x for x in o ]
    else:
      return [ o ]

  # http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
  @classmethod
  def chunks(clazz, l, n):
    'Yield successive n-sized chunks from l.'
    for i in range(0, len(l), n):
      yield l[i:i + n]

  @classmethod
  def flatten_list_of_lists(clazz, lol):
    return list(chain(*lol))

  @classmethod
  def without_none(clazz, c):
    'Return a list for the collection without None.'
    return [ x for x in c if x != None ]

  @classmethod
  def is_iterable(clazz, o):
    'Return True if o is iterable.'
    try:
      iter(o)
      return True
    except:
      return False

  @classmethod
  def is_homogeneous(clazz, l, t):
    'Return True if l is iterable and all its items are of a given type.'
    try:
      for x in iter(l):
        if not isinstance(x, t):
          return False
      return True
    except:
      return False

  @classmethod
  def are_callable(clazz, l):
    'Return True if all items in a list are callable.'
    return False not in [ callable(x) for x in clazz.listify(l) ]
