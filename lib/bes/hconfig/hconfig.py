#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint

from bes.system.log import logger

_log = logger('hconfig')

class hsection(object):

  def __init__(self, d):
    _log.log_d(f'hsection.__init__({pprint.pformat(d)})')
    self._dict = d

  def __str__(self):
    return pprint.pformat(self._dict)

  def __repr__(self):
    return str(self)
  
  def __getattribute__(self, key):
    _log.log_d(f'hsection.__getattribute__({key})')
    d = super().__getattribute__('_dict')
    if key not in d:
      raise AttributeError(f'No key \"{key}\" found')
    value = d.get(key)
    if isinstance(value, dict):
      return hsection(value)
    return value

class hconfig(hsection):

  def __init__(self, d):
    _log.log_d(f'hconfig.__init__({pprint.pformat(d)})')
    super().__init__(copy.deepcopy(d))
