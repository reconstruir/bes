#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.string_util import string_util

from .btl_parsing import btl_parsing

class btl_desc_state_command(namedtuple('btl_desc_state_command', 'name, command, args')):
  
  def __new__(clazz, name, command, args):
    check.check_string(name)
    check.check_string(command)
    check.check_dict(args, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, name, command, args)

  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    parts = string_util.split_by_white_space(n.data.text, strip = True)
    name = parts.pop(0)
    command = parts.pop(0)
    args = clazz._parse_key_values(parts)
    return btl_desc_state_command(name, command, args)

  def generate_code(self, buf):
    check.check_btl_code_gen_buffer(buf)

    if self.name == 'emit':
      buf.write_line(f'tokens.append(self.make_token(\'{self.command}\', args = {self.args}))')
    elif self.name == 'buffer':
      if self.command == 'write':
        buf.write_line(f'self.buffer_write(c)')
      elif self.command == 'reset':
        buf.write_line(f'self.buffer_reset()')
      else:
        buf.write_line(f'''raise btl_lexer_error('Unknown buffer command: "{self.command}"')''')

  @classmethod
  def _parse_key_value(clazz, s):
    key, delim, value = s.partition('=')
    return ( key.strip(), value.strip() )
        
  @classmethod
  def _parse_key_values(clazz, parts):
    result = {}
    for part in parts:
      key, value = clazz._parse_key_value(part)
      result[key] = value
    return result
        
check.register_class(btl_desc_state_command, include_seq = False)
