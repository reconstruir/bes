# -*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from datetime import datetime
from datetime import timedelta
from typing import Any
import typing

class bcli_typing(object):
  
  _SIMPLE_TYPES = {
    'int': int,
    'str': str,
    'bool': bool,
    'float': float,
    'list': list,
    'set': set,
    'dict': dict,
    'tuple': tuple,
#    'any': typing.Any
    'datetime': datetime,
    'timedelta': timedelta,
  }

  @classmethod
  def parse_type(clazz, type_str: str) -> typing.Any:
    """Parses a string representing a type into the corresponding Python type."""
    try:
      # Handle generic types with parameters, e.g., list[str], set[int]
      if '[' in type_str and ']' in type_str:
        base_type_str, param_str = type_str.split('[', 1)
        param_str = param_str.rstrip(']')
        base_type = clazz._SIMPLE_TYPES.get(base_type_str)

        if base_type:
          # Split parameters if there are multiple, e.g., dict[str, int]
          params = [ clazz.parse_type(param.strip()) for param in param_str.split(',') ]
          if base_type in { list, typing.List }:
            return typing.List[params[0]]
          elif base_type in { set, typing.Set }:
            return typing.Set[params[0]]
          elif base_type in { dict, typing.Dict }:
            return typing.Dict[params[0], params[1]]
          elif base_type in { tuple, typing.Tuple }:
            return typing.Tuple[tuple(params)]
      else:
        # Handle simple types, e.g., int, str
        return clazz._SIMPLE_TYPES[type_str]
    except Exception as e:
      raise ValueError(f"Invalid type string: {type_str}") from e
'''
# Examples of parsing type strings
print(parse_type("int"))      # Output: <class 'int'>
print(parse_type("bool"))       # Output: <class 'bool'>
print(parse_type("list[str]"))    # Output: typing.List[str]
print(parse_type("set[int]"))     # Output: typing.Set[int]
print(parse_type("dict[str, int]")) # Output: typing.Dict[str, int]
'''
