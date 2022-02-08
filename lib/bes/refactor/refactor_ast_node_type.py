#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.enum_util.checked_enum import checked_enum

class refactor_ast_node_type(checked_enum):
  CLASS = 'class'
  CLASS_FUNCTION = 'class_function'
  FUNCTION = 'function'
  #COMMENT = 'comment'
  #DOC_STRING = 'doc_string'

refactor_ast_node_type.register_check_class()
  
