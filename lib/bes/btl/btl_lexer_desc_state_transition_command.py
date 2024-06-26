#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.string_util import string_util

from .btl_lexer_error import btl_lexer_error
from .btl_lexer_desc_error_list import btl_lexer_desc_error_list

from .btl_desc_command import btl_desc_command

class btl_lexer_desc_state_transition_command(btl_desc_command):
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    if self.name == 'emit':
      buf.write_line(f'tokens.append(self.make_token(context, {self.action_resolved}))')
    elif self.name == 'buffer':
      if self.action == 'write':
        buf.write_line(f'context.buffer_write(c)')
      elif self.action == 'reset':
        buf.write_line(f'context.buffer_reset()')
      else:
        raise btl_lexer_error(f'Unknown command action: "{self.action}"')
    elif self.name == 'error':
      error = errors.find_error(self.action)
      if not error:
        raise btl_lexer_error(f'Unknown error: {self.action}')
      buf.write_line(f"""message = f'{error.message}'""")
      buf.write_line(f'raise self.lexer.{error.error_class_name}(context, message)')
    elif self.name == 'function':
      if self.args:
        flat_args = ', '.join(list(self.args))
        args_part = f', {flat_args}'
      else:
        args_part = f''
      buf.write_line(f'self.lexer._function_{self.action}(self).call(context, tokens, c{args_part})')
    else:
      raise btl_lexer_error(f'Unknown command: {self.name}')
        
check.register_class(btl_lexer_desc_state_transition_command, include_seq = False)
