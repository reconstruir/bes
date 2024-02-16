#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..text.tree_text_parser import _text_node

from .btl_error import btl_error

class btl_desc_text_node(_text_node):

  def parse_key_value(self, source, result_class = None, delimiter = ':'):
    check.check_string(source)
    check.check_string(delimiter)
    check.check_class(result_class, allow_none = True)

    key, delim, value = self.data.text.partition(delimiter)
    key = key.strip()
    value = value.strip()
    if delimiter == ' ':
      value = value or None
    else:
      if delim != delimiter:
        raise btl_error(f'Invalid key value "{self.data.text}" at {source}:{self.data.line_number}')
    
    if result_class:
      return result_class(key, value)
    return key, value

  def find_tree_section(self, name, source, raise_error = True):
    assert name
    assert source
    section_node = self.find_child_by_text(name)
    if raise_error and not section_node:
      raise btl_error(f'Missing section "{name}" from "{source}"')
    return section_node
