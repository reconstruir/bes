#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

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

  @cached_property
  def as_sorted_list(self):
    return sorted([ token.name for token in self ])
    
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

  def generate_code(self, buf, namespace, name):
    check.check_btl_code_gen_buffer(buf)
    check.check_string(namespace)
    check.check_string(name)

    buf.write_line(f'''
class {namespace}_{name}_lexer_token(object):
''')
    
    with buf.indent_pusher() as _:
      buf.write_lines(f'''def __init__(self, lexer):
  check.check_text_lexer(lexer)

  self._lexer = lexer
''')      
    
    with buf.indent_pusher() as _:
      for token in self:
        token.generate_code(buf)
    
btl_desc_token_list.register_check_class()
