#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
import typing

from datetime import datetime
from datetime import timedelta

#from typing import Any

from collections import namedtuple

from bes.system.check import check
from bes.property.cached_property import cached_property

from .bcli_simple_type_item import bcli_simple_type_item

class bcli_simple_type_manager(object):

  _BASIC_TYPES = [
    bcli_simple_type_item('int', lambda: int,  lambda: None),
    bcli_simple_type_item('str', lambda: str, lambda: None),
    bcli_simple_type_item('bool', lambda: bool, lambda: None),
    bcli_simple_type_item('float', lambda: float, lambda: None),
    bcli_simple_type_item('list', lambda: list, lambda: None),
    bcli_simple_type_item('set', lambda: set, lambda: None),
    bcli_simple_type_item('dict', lambda: dict, lambda: None),
    bcli_simple_type_item('tuple', lambda: tuple, lambda: None),
    bcli_simple_type_item('datetime', lambda: datetime, lambda: None),
    bcli_simple_type_item('timedelta', lambda: timedelta, lambda: None),
  ]
  
  def __init__(self):
    self._types = {}
    for t in self._BASIC_TYPES:
      self.add_type(t)
      
  def add_type(self, t):
    check.check_bcli_simple_type_item(t)

    if t.name in self._types:
      raise KeyError(f'type "{t.name}" already added.')
    self._types[t.name] = t

  def default(self, type_name):
    check.check_string(type_name)

    t = self._types.get(type_name, None)
    if not t:
      raise KeyError(f'type "{type_name}" not found.')
    return t.default

  def type(self, type_name):
    check.check_string(type_name)

    t = self._types.get(type_name, None)
    if not t:
      raise KeyError(f'type "{type_name}" not found.')
    return t.type

  @classmethod
  def _parse_type_str(clazz, type_str: str) -> typing.Tuple[str, str]:
    f = re.findall(r'(\w+)\s*\[\s*(\w+)\s*\]', type_str)
    if not f:
      return ( type_str.strip(), None )
    if len(f) != 1:
      return None
    if len(f[0]) != 2:
      return None
    return f[0]
  
check.register_class(bcli_simple_type_manager, include_seq = False)    
