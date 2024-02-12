#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check

from .btl_parser_desc_state_command_list import btl_parser_desc_state_command_list
from .btl_parser_desc_state_transition_list import btl_parser_desc_state_transition_list
from .btl_parsing import btl_parsing

class btl_parser_desc_state(namedtuple('btl_parser_desc_state', 'name, transitions, commands, one_time_commands')):
  
  def __new__(clazz, name, transitions, commands, one_time_commands):
    check.check_string(name)

    transitions = check.check_btl_parser_desc_state_transition_list(transitions)
    commands = check.check_btl_parser_desc_state_command_list(commands)
    one_time_commands = check.check_btl_parser_desc_state_command_list(one_time_commands)
    return clazz.__bases__[0].__new__(clazz,
                                      name,
                                      transitions,
                                      commands,
                                      one_time_commands)

  def to_dict(self):
    return {
      'name': self.name,
      'transitions': self.transitions.to_dict_list(),
      'commands': self.commands.to_dict_list(),
      'one_time_commands': self.one_time_commands.to_dict_list(),
    }
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)

    name = n.data.text.strip()
    transitions_node = btl_parsing.find_tree_section(n,
                                                     'transitions',
                                                     source,
                                                     raise_error = False)
    transitions = btl_parser_desc_state_transition_list.parse_node(transitions_node,
                                                                   source = source)

    commands_node = btl_parsing.find_tree_section(n,
                                                  'commands',
                                                  source,
                                                  raise_error = False)
    commands = btl_parser_desc_state_command_list.parse_node(commands_node, source = source)

    one_time_commands_node = btl_parsing.find_tree_section(n,
                                                           'one_time_commands',
                                                           source,
                                                           raise_error = False)
    one_time_commands = btl_parser_desc_state_command_list.parse_node(one_time_commands_node,
                                                                      source = source)

    return btl_parser_desc_state(name, transitions, commands, one_time_commands)

  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    buf.write_lines(f'''
class _state_{self.name}(btl_parser_state_base):
  def __init__(self, parser, log_tag):
    name = '{self.name}'
    super().__init__(parser, name, log_tag)
''')

    buf.write_lines(f'''
  def enter_state(self, context):
    self.log_d(f'{self.name}: enter_state')
''')
    
    buf.write_lines(f'''
  def leave_state(self, context):
    self.log_d(f'{self.name}: leave_state')
''')
    
    buf.write_lines(f'''
  def handle_token(self, context, token, first_time):
    self.log_handle_token(token)
    new_state_name = None
''')

    if self.one_time_commands:
      with buf.indent_pusher(depth = 2) as _:
        buf.write_lines(f'''
if first_time:
''')
        with buf.indent_pusher(depth = 1) as _:
          self.one_time_commands.generate_code(buf, errors)
        buf.write_linesep()
        
    if self.commands:
      with buf.indent_pusher(depth = 2) as _:
        self.commands.generate_code(buf, errors)
        buf.write_linesep()
        
    with buf.indent_pusher(depth = 2) as _:
      self.transitions.generate_code(buf, errors)
      buf.write_lines(f'''
return new_state_name
''')
  
check.register_class(btl_parser_desc_state, include_seq = False)
