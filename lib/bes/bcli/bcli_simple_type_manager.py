#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
import typing

from datetime import datetime
from datetime import timedelta

#from typing import Any

from collections import namedtuple

from bes.system.check import check
from bes.property.cached_property import cached_property
from bes.common.variable import variable

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
    self._variables = {}
    self._defaults = {}

  def add_variable(self, name, function):
    check.check_string(name)
    check.check_callable(function)

    assert name not in self._variables
    self._variables[name] = function

  def add_variables(self, variables):
    check.check_dict(variables, key_type = str)

    for name, function in variables.items():
      self.add_variable(name, function)

  def add_default(self, name, function):
    check.check_string(name)
    check.check_callable(function)

    assert name not in self._defaults
    self._defaults[name] = function

  def add_defaults(self, defaults):
    check.check_dict(defaults, key_type = str)

    for name, function in defaults.items():
      self.add_default(name, function)

  def has_default(self, name):
    check.check_string(name)

    return name in self._defaults

  def default(self, name):
    check.check_string(name)

    return self._defaults[name]
  
  def substitute_variables(self, s):
    return variable.substitute(s, self._variables)
    
  def add_type(self, t):
    check.check_bcli_simple_type_item(t)

    if t.name in self._types:
      raise KeyError(f'type "{t.name}" already added.')
    self._types[t.name] = t

  def add_types(self, types):
    types = check.check_bcli_simple_type_item_list(types)
    for t in types:
      self.add_type(t)
    
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
    base_type = self._types[base_str].type
    #print(f'base_str={base_str} param_str={param_str} base_type={base_type}')
    if not param_str:
      t = self._types.get(base_str, None)
      if not t:
        raise ValueError(f'simple type "{base_str}" not found.')
      return t.type

    # Split parameters if there are multiple, e.g., dict[str, int]
    params = [ self._parse_type_str_to_typing(param.strip()) for param in param_str.split(',') ]
    params_type = [ param for param in params ]
    #print(f'params={params}')
    if base_type in { list, typing.List }:
      return typing.List[params_type[0]]
    elif base_type in { set, typing.Set }:
      return typing.Set[params_type[0]]
    elif base_type in { dict, typing.Dict }:
      return typing.Dict[params_type[0], params_type[1]]
    elif base_type in { tuple, typing.Tuple }:
      return typing.Tuple[tuple(params_type)]
    else:
      raise ValueError(f'base_type "{base_type}" not found.')

  @classmethod
  def check_instance(clazz, value, type_hint):
    origin = typing.get_origin(type_hint)
    args = typing.get_args(type_hint)

    if origin is None:  # Simple types
      return isinstance(value, type_hint)
    elif origin is list:  # List with a specific type
      if isinstance(value, list) and len(args) == 1:
        return all(isinstance(item, args[0]) for item in value)
    elif origin is dict:  # Dict with specific key-value types
      if isinstance(value, dict) and len(args) == 2:
        return all(isinstance(k, args[0]) and isinstance(v, args[1]) for k, v in value.items())
    elif origin is set:  # Set with a specific type
      if isinstance(value, set) and len(args) == 1:
        return all(isinstance(item, args[0]) for item in value)
    elif origin is tuple:  # Tuple with specific types
      if isinstance(value, tuple) and len(args) == len(value):
        return all(isinstance(item, arg) for item, arg in zip(value, args))

    return False
    
check.register_class(bcli_simple_type_manager, include_seq = False)    
