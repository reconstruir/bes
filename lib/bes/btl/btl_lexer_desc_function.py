#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check
from ..common.string_util import string_util

from .btl_lexer_error import btl_lexer_error

from .btl_desc_function_base import btl_desc_function_base

class btl_lexer_desc_function(btl_desc_function_base):
  
  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    if self.args:
      flat_args = ', '.join(list(self.args))
      args_part = f', {flat_args}'
    else:
      args_part = f''

    buf.write_lines(f'''
class _function_{self.name}(btl_function_base):
  def call(self, context, tokens{args_part}):
''')
    with buf.indent_pusher(depth = 2) as _:
      self.commands.generate_code(buf, errors)
                    
check.register_class(btl_lexer_desc_function, include_seq = False)
