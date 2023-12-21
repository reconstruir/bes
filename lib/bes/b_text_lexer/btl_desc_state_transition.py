#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_error import btl_error
from .btl_parsing import btl_parsing

from .btl_desc_state_command_list import btl_desc_state_command_list

class btl_desc_state_transition(namedtuple('btl_desc_state_transition', 'to_state, char_name, commands')):
  
  def __new__(clazz, to_state, char_name, commands):
    check.check_string(to_state)
    check.check_string(char_name)
    commands = check.check_btl_desc_state_command_list(commands)
    return clazz.__bases__[0].__new__(clazz, to_state, char_name, commands)

  def to_dict(self):
    return {
      'to_state': self.to_state,
      'char_name': self.char_name,
      'commands': self.commands.to_dict_list(),
    }
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)

    char_name, to_state = btl_parsing.parse_key_value(n, source, delimiter = ':')
    commands = btl_desc_state_command_list.parse_node(n, source = source)
    return btl_desc_state_transition(to_state, char_name, commands)

check.register_class(btl_desc_state_transition, include_seq = False)
