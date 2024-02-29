#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.string_util import string_util

from .btl_lexer_error import btl_lexer_error

class btl_desc_command(object):
  
  def __init__(self, name, action, args):
    check.check_string(name)
    check.check_string(action)
    check.check_dict(args, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)

    self._name = name
    self._action = action
    self._args = args

  @property
  def name(self):
    return self._name

  @property
  def action(self):
    return self._action

  @property
  def args(self):
    return self._args
  
  def to_dict(self):
    return {
      'name': self.name,
      'action': self.action,
      'args': self.args,
    }

  def to_tuple(self):
    return ( self.name, self.action, self.args )
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    parts = string_util.split_by_white_space(n.data.text, strip = True)
    name = parts.pop(0)
    if not parts:
      raise btl_lexer_error(f'Missing arguments for command: "{name}" - line {n.data.line_number}')
    action = parts.pop(0)
    args = clazz._parse_key_values(parts)
    return clazz(name, action, args)
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)

    assert False, f'Not Implemented'

  @classmethod
  def _parse_key_value(clazz, s):
    key, delim, value = s.partition('=')
    return ( key.strip(), value.strip() )
        
  @classmethod
  def _parse_key_values(clazz, parts):
    result = {}
    for part in parts:
      key, value = clazz._parse_key_value(part)
      result[key] = value
    return result
