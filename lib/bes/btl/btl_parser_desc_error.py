#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_parsing import btl_parsing

class btl_parser_desc_error(namedtuple('btl_parser_desc_error', 'name, message')):
  
  def __new__(clazz, name, message):
    check.check_string(name)
    check.check_string(message)
    return clazz.__bases__[0].__new__(clazz, name, message)

  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    return btl_parsing.parse_key_value(n,
                                       source,
                                       result_class = btl_parser_desc_error)
  
check.register_class(btl_parser_desc_error)
