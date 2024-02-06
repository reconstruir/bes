#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_parser_desc_state_command import btl_parser_desc_state_command
from .btl_desc_command_list import btl_desc_command_list

class btl_parser_desc_state_command_list(btl_desc_command_list):

  __value_type__ = btl_parser_desc_state_command
  
  def __init__(self, values = None):
    super().__init__(values = values)

btl_parser_desc_state_command_list.register_check_class()
