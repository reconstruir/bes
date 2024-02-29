#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.string_util import string_util

from .btl_lexer_error import btl_lexer_error
from .btl_lexer_desc_error_list import btl_lexer_desc_error_list

from .btl_desc_variable_base import btl_desc_variable_base

class btl_lexer_desc_variable(btl_desc_variable_base):
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    if self.name == 'emit':
      buf.write_line(f'tokens.append(self.make_token(context, \'{self.action}\', args = {self.args}))')
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
    else:
      raise btl_lexer_error(f'Unknown command: {self.name}')
        
check.register_class(btl_lexer_desc_variable, include_seq = False)
