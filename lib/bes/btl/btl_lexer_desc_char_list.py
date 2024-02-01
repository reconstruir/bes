#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from os import path

from ..system.check import check
from ..common.type_checked_list import type_checked_list

from .btl_lexer_desc_char import btl_lexer_desc_char

class btl_lexer_desc_char_list(type_checked_list):

  __value_type__ = btl_lexer_desc_char
  
  def __init__(self, values = None):
    super().__init__(values = values)

  def to_dict_list(self):
    result = []
    for char in self:
      char_dict = char.to_dict()
      result.append(char_dict)
    return result
    
check.register_class(btl_lexer_desc_char_list, include_seq = False)
