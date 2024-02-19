#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_lexer_desc_variable import btl_lexer_desc_variable

from .btl_desc_variable_list import btl_desc_variable_list

class btl_lexer_desc_variable_list(btl_desc_variable_list):

  __value_type__ = btl_lexer_desc_variable
  
btl_lexer_desc_variable_list.register_check_class()
