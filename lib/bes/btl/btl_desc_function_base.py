#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_lexer_desc_state_transition_command_list import btl_lexer_desc_state_transition_command_list

class btl_desc_function_base(object):
  
  def __init__(self, name, commands):
    check.check_string(name)
    commands = check.check_btl_lexer_desc_state_transition_command_list(commands)

    self._name = name
    self._commands = commands

  @property
  def name(self):
    return self._name

  @property
  def commands(self):
    return self._commands
  
  def to_dict(self):
    return {
      'name': self.name,
      'commands': self.commands.to_dict_list(),
    }

  def to_tuple(self):
    return ( self.name, self.commands )
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)
    
    name = n.data.text.strip()
    commands = btl_lexer_desc_state_transition_command_list.parse_node(n, source = source)
    return clazz(name, commands)
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)

    assert False, f'Not Implemented'
