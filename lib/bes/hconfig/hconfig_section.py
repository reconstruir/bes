#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import copy
import pprint

from ..system.log import logger
from ..system.check import check

from .hconfig_error import hconfig_error

_log = logger('hconfig')

class hconfig_section(object):

  def __init__(self, d, root, path):
    _log.log_d(f'hconfig_section.__init__({pprint.pformat(d)})')
    self._dict = d
    self._root = root
    self._path = path

  def __str__(self):
    return pprint.pformat(super().__getattribute__('_dict'))

  def __repr__(self):
    return str(self)

  def _super_getattribute(self, key):
    return super().__getattribute__(key)
  
  def __getattribute__(self, key):
    _log.log_d(f'hconfig_section.__getattribute__({key})')
    d = super().__getattribute__('_dict')
    if key not in d:
      raise hconfig_error(f'No key \"{key}\" found')
    value = d.get(key)
    _path = super().__getattribute__('_path')
    _root = super().__getattribute__('_root')
    if _path != None:
      _path = _path + '.' + key
    else:
      _path = key
    _log.log_d(f'hconfig_section.__init__({pprint.pformat(d)})')
#    _log.log_d(f'hconfig_section.__getattribute__(): _path={_path} _root={id(_root)}')
    if isinstance(value, dict):
      value_for_caster = hconfig_section(value, _root, _path)
    else:
      value_for_caster = value
    caster = _root.find_caster(_path)
    if caster:
      return caster.cast_value(value_for_caster)
    return value_for_caster

check.register_class(hconfig_section, include_seq = False)
