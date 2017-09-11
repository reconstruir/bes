#!/usr/bin/env python
#-*- coding:utf-8 -*-

import copy

class dict_util(object):
  'Dict util'

  @staticmethod
  def combine(*dicts):
    result = {}
    for i, n in enumerate(dicts):
      if not isinstance(n, dict):
        raise TypeError('Argument %d is not a dict' % (i + 1))
      result.update(copy.deepcopy(n))
    return result

  @staticmethod
  def update(d, *dicts):
    for i, n in enumerate(dicts):
      if not isinstance(n, dict):
        raise TypeError('Argument %d is not a dict' % (i + 1))
      d.update(copy.deepcopy(n))

  @staticmethod
  def dump(d):
    longest_key = max([ len(key) for key in d.keys() ])
    fmt = '%%%ds: %%s' % (longest_key)
    for k, v in sorted(d.items()):
      print(fmt % (k, v))

  @staticmethod
  def filter_with_keys(d, keys):
    'Return a dict with only keys.'
    return { k: v for k,v in d.items() if k in keys }

  @staticmethod
  def is_homogeneous(d, key_type, value_type):
    'Return True if all items in d are of the given key_type and value_type.'
    for key, value in d.items():
      if not isinstance(key, key_type):
        return False
      if not isinstance(value, value_type):
        return False
    return True
