#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..system.check import check
from ..version.semantic_version import semantic_version

from .btl_parsing import btl_parsing

class btl_desc_state_command(namedtuple('btl_desc_state_command', 'name, arg')):
  
  def __new__(clazz, name, arg):
    check.check_string(name)
    check.check_string(arg, allow_none = True)
    return clazz.__bases__[0].__new__(clazz, name, arg)

  def to_dict(self):
    return dict(self._asdict())
  
  @classmethod
  def parse_node(clazz, n, source = '<unknown>'):
    check.check_node(n)
    check.check_string(source)

    return btl_parsing.parse_key_value(n,
                                       source,
                                       result_class = btl_desc_state_command,
                                       delimiter = ' ')

  def write_to_buffer(self, buf):
    check.check_btl_code_gen_buffer(buf)

    if self.name == 'yield':
      buf.write_line(f'tokens.append(self.make_token({self.arg}, self.buffer_value(), self.position)')
    elif self.name == 'buffer':
      if self.arg == 'write':
        buf.write_line(f'self.lexer.buffer_write(c)')
      elif self.arg == 'reset':
        buf.write_line(f'self.lexer.buffer_reset()')
      else:
        buf.write_line(f'''raise btl_lexer_error('Unknown buffer command: "{self.arg}"')''')
  
check.register_class(btl_desc_state_command)
