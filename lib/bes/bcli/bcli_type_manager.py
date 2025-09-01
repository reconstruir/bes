#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import re
import typing

from collections import namedtuple

from bes.system.check import check
from bes.system.log import logger
from bes.common.variable import variable
from bes.common.json_util import json_util

from .bcli_type_i import bcli_type_i

from .types.bcli_type_bool import bcli_type_bool
from .types.bcli_type_callable import bcli_type_callable
from .types.bcli_type_type import bcli_type_type
from .types.bcli_type_datetime import bcli_type_datetime
from .types.bcli_type_dict import bcli_type_dict
from .types.bcli_type_float import bcli_type_float
from .types.bcli_type_int import bcli_type_int
from .types.bcli_type_list import bcli_type_list
from .types.bcli_type_set import bcli_type_set
from .types.bcli_type_str import bcli_type_str
from .types.bcli_type_timedelta import bcli_type_timedelta
from .types.bcli_type_tuple import bcli_type_tuple

from .bcli_type_manager_error import bcli_type_manager_error

class bcli_type_manager(object):

  _log = logger('bcli')
  
  _BASIC_TYPES = [
    bcli_type_bool,
    bcli_type_callable,
    bcli_type_type,
    bcli_type_datetime,
    bcli_type_dict,
    bcli_type_float,
    bcli_type_int,
    bcli_type_list,
    bcli_type_set,
    bcli_type_str,
    bcli_type_timedelta,
    bcli_type_tuple,
  ]
  
  def __init__(self):
    self._types = {}
    for t in self._BASIC_TYPES:
      self.add_type(t)
    self._variables = {}

  def to_dict(self):
    return {
      'types': self._types,
      'variables': self._variables,
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)
  
  def add_variable(self, name, function):
    check.check_string(name)
    check.check_callable(function)

    #self._log.log_method_d()
    
    assert name not in self._variables
    self._variables[name] = function

  def add_variables(self, variables):
    check.check_dict(variables, key_type = str)

    for name, function in variables.items():
      self.add_variable(name, function)

  def substitute_variables(self, s):
    check.check_string(s)

    return variable.substitute(s, self._variables)

  def substitute_single_variable(self, s):
    check.check_string(s)

    name = variable.single_variable_name(s)
    if not name:
      return None
    if not name in self._variables:
      raise KeyError(f'variable "{name}" not found.')
    func = self._variables[name]
    assert check.is_callable(func)
    return func()
  
  def add_type(self, t):
    check.check_class(t)
    self._log.log_method_d()

    if not issubclass(t, bcli_type_i):
      raise TypeError(f't should be a subclass of bcli_type_i instead of "{t}".')
    
    if t.name in self._types:
      raise KeyError(f'type "{t.name}" already added.')
    self._types[t.name] = t

  def add_types(self, types):
    #types = check.check_seq(types, bcli_type_i)
    for t in types:
      self.add_type(t)
    
  def type(self, type_name):
    check.check_string(type_name)

    t = self._types.get(type_name, None)
    if not t:
      raise KeyError(f'type "{type_name}" not found.')
    return t.type

  _parsed_type = namedtuple('_parsed_type', 'base, parameter')
  @classmethod
  def _parse_type_str(clazz, type_str: str) -> typing.Tuple[str, str]:
    f = re.findall(r'(\w+)\s*\[\s*(\w+)\s*\]', type_str)
    if not f:
      return clazz._parsed_type(type_str.strip(), None)
    if len(f) != 1:
      return None
    if len(f[0]) != 2:
      return None
    base, parameter = f[0]
    #typing_type = self._parse_type_str_to_typing(type_str)
    return clazz._parsed_type(base, parameter)

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

  #@classmethod
  def check_instance(self, value, type_hint):
#    assert False
    origin = typing.get_origin(type_hint)
    args = typing.get_args(type_hint)

#    print(f'origin={origin} args={args} type_hint={type_hint}')
    if type_hint and type_hint in self._types:
      assert False

#    if self._types = {}
#
#    if item.option_type.check_function:
#      return item.option_type.check_function(value, allow_none = True)

    if origin is None:  # Simple types
      if check.is_callable(value):
        return True
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
    
check.register_class(bcli_type_manager, include_seq = False)    
