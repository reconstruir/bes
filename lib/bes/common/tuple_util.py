#!/usr/bin/env python
#-*- coding:utf-8 -*-

from collections import namedtuple
from functools import reduce

class tuple_util(object):
  'Tuple util'

  @staticmethod
  def dict_to_named_tuple(name, d):
    '''
    Create a namedtuple from a dictionary.  Any invalid keys are ignored.
    Inspired by https://gist.github.com/href/1319371
    '''

    def key_is_valid(key):
      try:
        if not key[0].isalpha():
          return False
        if len(key) == 1:
          return True
        return reduce(lambda a,b: a and b, [ c.isalnum() or c == '_' for c in key[1:] ])
      except:
        return False

    invalid_keys = [ k for k in d.keys() if not key_is_valid(k) ]
    valid_dict = { k: d[k] for k in d if k not in invalid_keys }
    return namedtuple(name, valid_dict.keys())(**valid_dict)
