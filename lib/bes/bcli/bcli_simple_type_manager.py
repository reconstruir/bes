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
    bcli_simple_type_item('int', lambda: int),
    bcli_simple_type_item('str', lambda: str),
    bcli_simple_type_item('bool', lambda: bool),
    bcli_simple_type_item('float', lambda: float),
    bcli_simple_type_item('list', lambda: list),
    bcli_simple_type_item('set', lambda: set),
    bcli_simple_type_item('dict', lambda: dict),
    bcli_simple_type_item('tuple', lambda: tuple),
    bcli_simple_type_item('datetime', lambda: datetime),
    bcli_simple_type_item('timedelta', lambda: timedelta),
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

  def _parse_type_str_to_typing(self, type_str: str) -> typing.Any:
    """Parses a string representing a type into the corresponding Python type."""

    base_str, param_str = self._parse_type_str(type_str)
    print(f'base_str={base_str} param_str={param_str}')
    if not param_str:
      t = self._types.get(base_str, None)
      if not t:
        raise ValueError(f'simple type "{base_str}" not found.')
      return t.type

    # Split parameters if there are multiple, e.g., dict[str, int]
    params = [ self._parse_type_str_to_typing(param.strip()) for param in param_str.split(',') ]
    print(f'params={params}')
    if base_str in { list, typing.List }:
      return typing.List[params[0]]
    elif base_str in { set, typing.Set }:
      return typing.Set[params[0]]
    elif base_str in { dict, typing.Dict }:
      return typing.Dict[params[0], params[1]]
    elif base_str in { tuple, typing.Tuple }:
      return typing.Tuple[tuple(params)]
    else:
      raise ValueError(f'base_str "{base_str}" not found.')
  
check.register_class(bcli_simple_type_manager, include_seq = False)    
