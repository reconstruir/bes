#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_desc_command import btl_desc_command
from .btl_lexer_desc_error_list import btl_lexer_desc_error_list

class btl_parser_desc_state_command(btl_desc_command):

  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)
    
    if self.name == 'create':
      buf.write_line(f'self.node_creator.create(\'{self._args[0]}\')')
    elif self.name == 'create_root':
      buf.write_line(f'self.node_creator.create_root()')
    elif self.name == 'set_token':
      buf.write_line(f'self.node_creator.set_token(\'{self._args[0]}\', token)')
    elif self.name == 'add_child':
      buf.write_line(f'self.node_creator.add_child(\'{self._args[0]}\', \'{self._args[1]}\')')
    else:
      buf.write_line(f'''raise btl_parser_error('Unknown buffer command: "{self.name}"')''')
        
check.register_class(btl_parser_desc_state_command, include_seq = False)
