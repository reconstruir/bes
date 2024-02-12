#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from ..system.check import check

from .btl_desc_command import btl_desc_command
from .btl_lexer_desc_error_list import btl_lexer_desc_error_list
from .btl_parser_error import btl_parser_error

class btl_parser_desc_state_transition_command(btl_desc_command):

  def generate_code(self, buf, errors):
    check.check_btl_code_gen_buffer(buf)
    errors = check.check_btl_lexer_desc_error_list(errors)

    if self.name == 'node':
      self._generate_node_command_code(buf, self.action, self.args)
    elif self.name == 'error':
      error = errors.find_error(self.action)
      if not error:
        raise btl_parser_error(f'Unknown error: {self.action}')
      buf.write_line(f'state_name = self.name')
      buf.write_line(f"""msg = f'{error.message}'""")
      buf.write_line(f'raise self.lexer.{error.error_class_name}(message = msg)')
    else:
      raise btl_parser_error(f'Unkown command: "{self.name}"')

  @classmethod
  def _generate_node_command_code(clazz, buf, action, args):
    quoted_args = [ f"'{arg}'" for arg in args ]
    flat_args = ', '.join(quoted_args)
    if action == 'create':
      buf.write_line(f'context.node_creator.create({flat_args})')
    elif action == 'create_root':
      buf.write_line(f'context.node_creator.create_root()')
    elif action == 'set_token':
      buf.write_line(f'context.node_creator.set_token({flat_args}, token)')
    elif action == 'add_child':
      buf.write_line(f'context.node_creator.add_child({flat_args})')
    else:
      raise btl_parser_error(f'Unkown "node" command action: "{action}"')
      
check.register_class(btl_parser_desc_state_transition_command, include_seq = False)
