#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
from collections import OrderedDict

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_error import btl_error

from .btl_parser_desc_state_transition_command_list import btl_parser_desc_state_transition_command_list

class btl_parser_desc_state_transition(namedtuple('btl_parser_desc_state_transition', 'to_state, token_name, commands')):
  
  def __new__(clazz, to_state, token_name, commands):
    check.check_string(to_state)
    check.check_string(token_name)
    commands = check.check_btl_parser_desc_state_transition_command_list(commands)
    return clazz.__bases__[0].__new__(clazz, to_state, token_name, commands)

  def to_dict(self):
    return {
      'to_state': self.to_state,
      'token_name': self.token_name,
      'commands': self.commands.to_dict_list(),
    }
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)

    token_name, to_state = n.parse_key_value(source, delimiter = ':')
    commands = btl_parser_desc_state_transition_command_list.parse_node(n, source = source)
    return btl_parser_desc_state_transition(to_state, token_name, commands)

  def generate_code(self, buf, errors, index, total):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)
    check.check_int(index)
    check.check_int(total)

    if_statement = 'if' if index == 0 else 'elif'
    
    token_name = self.token_name
    if token_name == 'default':
      if index == 0 and total == 1:
        buf.write_line(f'if True:')
      else:
        buf.write_line(f'else:')
    else:
      buf.write_line(f'{if_statement} token.name == \'{token_name}\':')
    with buf.indent_pusher() as _1:
      buf.write_line(f'new_state_name = \'{self.to_state}\'')
      self.commands.generate_code(buf, errors)
  
check.register_class(btl_parser_desc_state_transition, include_seq = False)
