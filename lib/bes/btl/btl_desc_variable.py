#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.string_util import string_util

from .btl_lexer_error import btl_lexer_error

class btl_desc_variable(object):
  
  def __init__(self, name, value):
    check.check_string(name)
    check.check_string(value)

    self.name = name
    self.value = value
    
  def to_dict(self):
    return {
      'name': self.name,
      'value': self.value,
    }

  def to_tuple(self):
    return ( self.name, self.value )
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    name, value = clazz._parse_key_value(n.data.text, delimiter = ':')
    return clazz(name, value)
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)

    assert False, f'Not Implemented'

  @classmethod
  def _parse_key_value(clazz, s, delimiter = '='):
    key, delim, value = s.partition(delimiter)
    assert delim.strip() == delimiter
    return ( key.strip(), value.strip() )
        
  @classmethod
  def _parse_key_values(clazz, parts):
    result = {}
    for part in parts:
      key, value = clazz._parse_key_value(part)
      result[key] = value
    return result
