#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple
import re

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

  @classmethod
  def _is_valid_first_char(clazz, c):
    return c.isalpha() or c == '_'

  @classmethod
  def _is_valid_char(clazz, c):
    return clazz._is_valid_first_char(c) or c.isnumeric()
  
  @classmethod
  def _is_valid_identifier(clazz, s):
    if not s:
      return False
    if not clazz._is_valid_first_char(s[0]):
      return False
    for c in s[1:]:
      if not clazz._is_valid_char(c):
        return False
    return True

  _declaration = namedtuple('_declaration', 'name, args')
  @classmethod
  def _parse_declaration(clazz, s):
    f = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)', s)
    if not f:
      return None
    if len(f) != 1:
      return None
    if len(f[0]) != 2:
      return None
    name = f[0][0].strip()
    args = f[0][1].split(',')
    args = [ arg.strip() for arg in args ]
    args = [ arg for arg in args if arg ]
    return clazz._declaration(name, tuple(args))
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)

    assert False, f'Not Implemented'
