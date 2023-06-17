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
    super().__setattr__('_dict', d)
    super().__setattr__('_root', root)
    super().__setattr__('_path', path)
    
#    self._dict = d
#    self._root = root
#    self._path = path

  def to_dict(self):
    return copy.deepcopy(super().__getattribute__('_dict'))
    
  def __str__(self):
    return pprint.pformat(super().__getattribute__('_dict'))

  def __repr__(self):
    return str(self)

  def _super_getattribute(self, key):
    return super().__getattribute__(key)

  def _super_setattr(self, key, value):
    return super().__setattr__(key, value)
  
  def __setattr__(self, key, value):
    self._dict[key] = value
#    d = super().__getattribute__('_dict')
#    d[key] = value
  
  def __getattribute__(self, key):
    _log.log_d(f'hconfig_section.__getattribute__({key})')
    d = super().__getattribute__('_dict')
    if key not in d:
      try:
        return super().__getattribute__(key)
      except AttributeError as ex:
        pass
      raise hconfig_error(f'No key \"{key}\" found')
    value = d.get(key)
    _path = super().__getattribute__('_path')
    _root = super().__getattribute__('_root')
    if _path != None:
      _path = _path + '.' + key
    else:
      _path = key
    _log.log_d(f'hconfig_section.__init__({pprint.pformat(d)})')
    if isinstance(value, list):
      value_for_caster = super().__getattribute__('_cast_list')(value, _path, _root)
    elif isinstance(value, dict):
      value_for_caster = hconfig_section(value, _root, _path)
    else:
      value_for_caster = value
    caster = _root.find_caster(_path)
    if caster:
      return caster.cast(value_for_caster, _root)
    return value_for_caster

  def _cast_list(self, value, path, root):
    result = []
    for i, item in enumerate(value):
      item_path = path + '.' + '_' + str(i)
      item_caster = root.find_caster(item_path)
      if isinstance(item, dict):
        value_for_caster = hconfig_section(item, root, item_path)
      else:
        value_for_caster = item
      if item_caster:
        casted_item = item_caster.cast(value_for_caster, root)
      else:
        casted_item = item
      result.append(casted_item)
    return result
  
check.register_class(hconfig_section, include_seq = False)
