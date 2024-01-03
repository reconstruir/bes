#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import OrderedDict

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list
from ..property.cached_property import cached_property

from .btl_desc_token import btl_desc_token
from .btl_error import btl_error
from .btl_parsing import btl_parsing

class btl_desc_token_list(type_checked_list):

  __value_type__ = btl_desc_token
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_sorted_list(self):
    return sorted(self._values, key = lambda token: token.name)
    
  def to_dict_list(self):
    return [ token for token in self.to_sorted_list() ]

  def find_token(self, name):
    for token in self:
      if token.name == name:
        return token
    return None
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)
    
    result = btl_desc_token_list()
    existing = set()
    for child in n.children:
      next_desc_token = btl_desc_token.parse_node(child, source)
      if next_desc_token.name in existing:
        raise btl_error(f'Duplicate token "{next_desc_token.name}" at {source}:{child.data.line_number}')
      result.append(next_desc_token)
    return sorted(result, key = lambda token: token.name)

  def generate_code(self, buf):
    check.check_btl_code_gen_buffer(buf)

    buf.write_line(f'class _token:')
    buf.write_linesep()
    with buf.indent_pusher() as _:
      for token in self:
        token.generate_code(buf)
    
btl_desc_token_list.register_check_class()
