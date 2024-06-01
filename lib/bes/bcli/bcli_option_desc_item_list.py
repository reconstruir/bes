#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.common.type_checked_list import type_checked_list
from bes.property.cached_property import cached_property
from bes.text.text_line_parser import text_line_parser

from .bcli_option_desc_item import bcli_option_desc_item

class bcli_option_desc_item_list(type_checked_list):

  __value_type__ = bcli_option_desc_item
  
  def __init__(self, values = None):
    super().__init__(values = values)

  @classmethod
  def parse_text(clazz, text):
    check.check_string(text)

    lines = text_line_parser.parse_lines(text,
                                         strip_comments = True, strip_text = True,
                                         remove_empties = True)
    result = bcli_option_desc_item_list()
    for line_text in lines:
      item = bcli_option_desc_item.parse_text(line_text)
      result.append(item)
      
    return result
  
  def to_dict(self):
    result = {}
    for item in self:
      assert item.name not in result
      result[item.name] = item
    return result
