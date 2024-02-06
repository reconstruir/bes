#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_parser_desc_state_transition_command import btl_parser_desc_state_transition_command
from .btl_desc_command_list import btl_desc_command_list

class btl_parser_desc_state_transition_command_list(btl_desc_command_list):

  __value_type__ = btl_parser_desc_state_transition_command

btl_parser_desc_state_transition_command_list.register_check_class()
