#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.string_util import string_util

from .btl_parsing import btl_parsing

class btl_desc_command(object):
  
  def __init__(self, name, action, args):
    check.check_string(name)
    check.check_string(action)
    check.check_dict(args, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)

    self.name = name
    self.action = action
    self.args = args
    
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
    command = parts.pop(0)
    args = clazz._parse_key_values(parts)
    return btl_desc_command(name, command, args)

  def generate_code(self, buf):
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
