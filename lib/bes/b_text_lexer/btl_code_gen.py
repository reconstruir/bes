#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os.path as path
from ..fs.file_util import file_util
from ..system.check import check
from ..system.log import logger
#from ..text.lexer_token import lexer_token

from .btl_code_gen_error import btl_code_gen_error
from .btl_code_gen_buffer import btl_code_gen_buffer

class btl_code_gen(object):

  _log = logger('btl')
  
  _HEADER = '''\
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.text.lexer_token import lexer_token
from bes.text.text_lexer_base import text_lexer_base
from bes.text.text_lexer_char import text_lexer_char
from bes.text.text_lexer_state_base import text_lexer_state_base
'''
  
  @classmethod
  def state_diagram_generate_code(clazz, filename, namespace, name, output_directory,
                                  indent = 2, skip_start_state = True, skip_end_state = True):
    filename = file_check.check_file(filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_string(output_directory)
    check.check_int(indent)

    mmd_doc = clazz.state_diagram_parse_file(filename, indent = indent)
    basename = f'{namespace}_{name}_lexer_detail.py'
    output_filename = path.join(output_directory, basename)
    file_util.mkdir(output_directory)
    with open(output_filename, 'w') as stream:
      stream.write(clazz._HEADER)
      stream.write(os.linesep)
      state_instance_code_list = []
      for state in mmd_doc.states:
        if skip_start_state and state == '__start':
          continue
        if skip_end_state and state == '__end':
          continue
        state_class_code = clazz._make_state_class_code(namespace,
                                                        name,
                                                        state,
                                                        mmd_doc.transitions.from_transitions())
        stream.write(state_class_code)
        stream.write(os.linesep)
        state_class_name = f'{namespace}_{name}_lexer_state_{state}'
        state_instance_code = f'self.{state} = {state_class_name}(self)'
        state_instance_code_list.append(state_instance_code)
      token_class_code = clazz._make_token_class_code(namespace,
                                                      name,
                                                      mmd_doc.tokens)
      stream.write(token_class_code)
      stream.write(os.linesep)
      lexer_class_code = clazz._LEXER_CLASS_TEMPLATE.format(namespace = namespace,
                                                            name = name,
                                                            state = state)
      stream.write(lexer_class_code)
      stream.write(os.linesep)
      for state_instance_code in state_instance_code_list:
        stream.write('    ')
        stream.write(state_instance_code)
        stream.write(os.linesep)
    return output_filename

  @classmethod
  def _make_state_machine_code(clazz, buf, namespace, name, desc):
    check.check_btl_code_gen_buffer(buf)
    check.check_string(namespace)
    check.check_string(name)
    check.check_btl_desc(desc)

    buf.write_line(f'''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.b_text_lexer.btl_lexer_base import btl_lexer_base
from bes.b_text_lexer.btl_lexer_state_base import btl_lexer_state_base
''')
    
  @classmethod
  def _make_token_class_code(clazz, buf, namespace, name, tokens):
    check.check_btl_code_gen_buffer(buf)
    check.check_string(namespace)
    check.check_string(name)

    buf.write_line(f'''
class {namespace}_{name}_lexer_token(object):
''')
    
    with buf.indent_pusher() as _1:
      for i, token_name in enumerate(sorted(tokens)):
        token_name_upper = token_name.upper()
        buf.write_line(f"{token_name_upper} = '{token_name}'")
    
      buf.write_lines(f'''
def __init__(self, lexer):
  check.check_text_lexer(lexer)

  self._lexer = lexer
''')

      for i, token_name in enumerate(sorted(tokens)):
        token_name_upper = token_name.upper()
        buf.write_lines(f'''
def make_{token_name}(self, value, position):
  return lexer_token(self.{token_name_upper}, value, self._lexer.position)
''')
  
  @classmethod
  def _make_state_class_code(clazz, buf, namespace, name, char_map, state):
    check.check_btl_code_gen_buffer(buf)
    check.check_string(namespace)
    check.check_string(name)
    check.check_btl_desc_char_map(char_map)
    check.check_btl_desc_state(state)

    buf.write_lines(f'''
class {namespace}_{name}_lexer_state_{state.name}(btl_lexer_state_base):
  def __init__(self, lexer):
    super().__init__(lexer)

  def handle_char(self, c):
    self.log_handle_char(c)

    new_state = None
    tokens = []

''')

    with buf.indent_pusher(depth = 2) as _:
      for transition in state.transitions:
        clazz._make_transition_code(buf, char_map, transition)

      buf.write_lines(f'''
self.lexer.change_state(new_state, c)
return tokens
''')
        
  @classmethod
  def _make_transition_code(clazz, buf, char_map, transition):
    check.check_btl_code_gen_buffer(buf)
    check.check_btl_desc_char_map(char_map)
    check.check_btl_desc_state_transition(transition)

    char_name = transition.char_name
    if char_name != 'default' and char_name not in char_map:
      raise btl_code_gen_error(f'char not found in char_map: "{char_name}"')
    char = char_map[char_name]

    buf.write_line(f'if c in {char.chars}:')
    with buf.indent_pusher() as _1:
      buf.write_line(f'new_state = {transition.to_state}')

      for command in transition.commands:
        clazz._make_state_command_code(buf, command)

  @classmethod
  def _make_state_command_code(clazz, buf, command):
    check.check_btl_code_gen_buffer(buf)
    check.check_btl_desc_state_command(command)

    if command.name == 'yield':
      buf.write_line(f'tokens.append(self.make_token({command.arg}, self.buffer_value(), self.position)')
    elif command.name == 'buffer':
      if command.arg == 'write':
        buf.write_line(f'self.lexer.buffer_write(c)')
      elif command.arg == 'reset':
        buf.write_line(f'self.lexer.buffer_reset()')
      else:
        buf.write_line(f'''raise btl_lexer_error('Unknown buffer command: "{command.arg}"')''')
