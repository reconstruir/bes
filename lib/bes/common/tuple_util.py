#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from functools import reduce

from .check import check

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

  @staticmethod
  def is_named_tuple(o):
    'Return True if o is a namedtuple.'
    return check.is_tuple(o) and getattr(o, '_fields', None) is not None

  @staticmethod
  def named_tuple_to_dict(o):
    'Convert a namedtuple to a dictionary.'
    if not tuple_util.is_named_tuple(o):
      raise TypeError('Not a namedtuple: {} - {}'.format(str(o), type(o)))
    return dict(o._asdict())
  
  @staticmethod
  def clone(t, mutations = None):
    mutations = mutations or {}
    'Clone a namedtuple with optional field mutations.'
    if not tuple_util.is_named_tuple(t):
      raise TypeError('not a namedtuple: %s - %s' % (str(t), type(t)))
    check.check_dict(mutations, key_type = check.STRING_TYPES)
    l = list(t)
    tuple_fields = t._fields
    for field, value in mutations.items():
      if field not in tuple_fields:
        raise ValueError('field \"%s\" not in tuple \"%s\"' % (field, str(t)))
      index = tuple_fields.index(field)
      l[index] = value
    return t.__class__(*l)

  @staticmethod
  def to_key_value_list(t):
    if not tuple_util.is_named_tuple(t):
      raise TypeError('not a namedtuple: %s - %s' % (str(t), type(t)))
    return [ ( key, value ) for ( key, value ) in zip(t._fields, list(t)) ]
