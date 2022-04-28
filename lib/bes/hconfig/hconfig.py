#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint

class hsection(object):

  def __init__(self, d):
    self._dict = d

  def __str__(self):
    return pprint.pformat(self._dict)

  def __repr__(self):
    return str(self)
  
  def __getattr__(self, key):
    if key not in self._dict:
      raise AttributeError(f'No key \"{key}\" found')
    value = self._dict[key]
    if isinstance(value, dict):
      value = caca(value, do_copy = False)
    return value


class hconfig(object):

  def __init__(self, d):
    pass #self._original_dict = copy.deepcopy(d)

  @classmethod
  def caca(clazz, d):
    self._dict = copy.deepcopy(d)
    
  def __str__(self):
    return self._dict.__str__()

  def __repr__(self):
    return self._dict.__repr__()
  
  def __getattr__(self, key):
    #print(f'key={key}')
    #s = pprint.pformat(self._dict)
    #print(f'dict={s}')
    if key not in self._dict:
      raise AttributeError(f'No key \"{key}\" found')
    value = self._dict[key]
    if isinstance(value, dict):
      value = caca(value, do_copy = False)
    return value
