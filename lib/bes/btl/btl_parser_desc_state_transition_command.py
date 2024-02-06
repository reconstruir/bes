#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_desc_command import btl_desc_command
from .btl_lexer_desc_error_list import btl_lexer_desc_error_list

class btl_parser_desc_state_transition_command(btl_desc_command):

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
        buf.write_line(f'''raise btl_parser_error('Unknown buffer command: "{self.action}"')''')
        
check.register_class(btl_parser_desc_state_transition_command, include_seq = False)
