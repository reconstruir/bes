#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_lexer_desc_function import btl_lexer_desc_function

from .btl_desc_function_list_base import btl_desc_function_list_base

class btl_lexer_desc_function_list(btl_desc_function_list_base):

  __value_type__ = btl_lexer_desc_function
  
btl_lexer_desc_function_list.register_check_class()
