#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version
from ..property.cached_property import cached_property

from .btl_parsing import btl_parsing

class btl_desc_token(namedtuple('btl_desc_token', 'name')):
  
  def __new__(clazz, name):
    check.check_string(name)

    return clazz.__bases__[0].__new__(clazz, name)

  @cached_property
  def name_upper(self):
    return self.name.upper()
  
  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    name = n.data.text.strip()
    return btl_desc_token(name)

  def generate_code(self, buf):
    check.check_btl_code_gen_buffer(buf)

    buf.write_line(f'{self.name_upper} = \'{self.name}\'')
    
check.register_class(btl_desc_token, include_seq = False)
