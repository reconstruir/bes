#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..common.string_util import string_util

from .btl_parsing import btl_parsing
from .btl_lexer_error import btl_lexer_error
from .btl_lexer_desc_error_list import btl_lexer_desc_error_list

class btl_lexer_desc_state_transition_command(namedtuple('btl_lexer_desc_state_transition_command', 'name, action, args')):
  
  def __new__(clazz, name, action, args):
    check.check_string(name)
    check.check_string(action)
    check.check_dict(args, check.STRING_TYPES, check.STRING_TYPES, allow_none = True)
    
    return clazz.__bases__[0].__new__(clazz, name, action, args)

  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    parts = string_util.split_by_white_space(n.data.text, strip = True)
    name = parts.pop(0)
    if not parts:
      raise btl_lexer_error(f'Missing arguments for command: "{name}" - line {n.data.line_number}')
    action = parts.pop(0)
    args = clazz._parse_key_values(parts)
    return btl_lexer_desc_state_transition_command(name, action, args)

  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    if self.name == 'emit':
      buf.write_line(f'tokens.append(self.make_token(\'{self.action}\', args = {self.args}))')
    elif self.name == 'buffer':
      if self.action == 'write':
        buf.write_line(f'self.buffer_write(c)')
      elif self.action == 'reset':
        buf.write_line(f'self.buffer_reset()')
      else:
        raise btl_lexer_error(f'Unknown command action: "{self.action}"')
    elif self.name == 'error':
      error = errors.find_error(self.action)
      if not error:
        raise btl_lexer_error(f'Unknown error: {self.action}')
      buf.write_line(f'state_name = self.name')
      buf.write_line(f'char = c')
      buf.write_line(f"""msg = f'{error.message}'""")
      buf.write_line(f'raise self.lexer.{error.error_class_name}(message = msg)')
    else:
      raise btl_lexer_error(f'Unknown command: {self.name}')

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
        
check.register_class(btl_lexer_desc_state_transition_command, include_seq = False)
