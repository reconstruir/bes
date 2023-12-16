#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_error import btl_error
from .btl_parsing import btl_parsing

from .btl_desc_state_command_list import btl_desc_state_command_list

class btl_desc_state_transition(namedtuple('btl_desc_state_transition', 'char, commands')):
  
  def __new__(clazz, char, commands):
    check.check_string(char)
    commands = check.check_btl_desc_state_command_list(commands)
    return clazz.__bases__[0].__new__(clazz, char, commands)

  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)

    print(f'n={n.data.text}')
    return None
    for child in n.children:
      key, value = btl_parsing.parse_key_value(child, source)
      if key not in d:
        raise btl_error(f'Invalid header key "{key}" at {source}:{child.data.line_number}')
      d[key] = value
    for key, value in d.items():
      if value == None:
        raise btl_error(f'Missing key "{key}" at {source}:{n.data.line_number}')
    return btl_desc_state_transition(*[ item[1] for item in d.items() ])

check.register_class(btl_desc_state_transition, include_seq = False)
