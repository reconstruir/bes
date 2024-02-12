#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from collections import namedtuple

from ..common.json_util import json_util
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..system.check import check
from ..text.tree_text_parser import tree_text_parser
from ..version.semantic_version import semantic_version

from .btl_code_gen_buffer import btl_code_gen_buffer
from .btl_error import btl_error
from .btl_parser_desc_char import btl_parser_desc_char
from .btl_parser_desc_error_list import btl_parser_desc_error_list
from .btl_parser_desc_header import btl_parser_desc_header
from .btl_parser_desc_mermaid import btl_parser_desc_mermaid
from .btl_parser_desc_state_command_list import btl_parser_desc_state_command_list
from .btl_parser_desc_state_list import btl_parser_desc_state_list
from .btl_parsing import btl_parsing

class btl_parser_desc(namedtuple('btl_parser_desc', 'header, errors, states, start_commands, end_commands, source_text')):
  
  def __new__(clazz,
              header,
              errors,
              states,
              start_commands,
              end_commands,
              source_text = None):
    header = check.check_btl_parser_desc_header(header)
    errors = check.check_btl_parser_desc_error_list(errors)
    states = check.check_btl_parser_desc_state_list(states)
    start_commands = check.check_btl_parser_desc_state_command_list(start_commands)
    end_commands = check.check_btl_parser_desc_state_command_list(end_commands)
    check.check_string(source_text, allow_none = True)

    source_text = source_text or ''
    return clazz.__bases__[0].__new__(clazz,
                                      header,
                                      errors,
                                      states,
                                      start_commands,
                                      end_commands,
                                      source_text)

  def to_dict(self):
    return {
      'header': self.header.to_dict(),
      'errors': self.errors.to_dict_list(),
      'states': self.states.to_dict_list(),
      'start_commands': self.start_commands.to_dict_list(),
      'end_commands': self.end_commands.to_dict_list(),
    }

  def to_json(self):
    return json_util.to_json(self.to_dict(), indent = 2, sort_keys = False)

  def to_mermaid_diagram(self):
    return btl_parser_desc_mermaid.desc_to_mermain_diagram(self)
  
  @classmethod
  def parse_text(clazz, text, source = '<unknown>'):
    check.check_string(text)
    check.check_string(source)

    root = tree_text_parser.parse(text, strip_comments = True, root_name = 'btl_parser_desc')

    parser_node = btl_parsing.find_tree_section(root, 'parser', source)
    header = btl_parser_desc_header.parse_node(parser_node, source)
    #print(header)

    errors_node = btl_parsing.find_tree_section(root, 'errors', source, raise_error = False)
    errors = btl_parser_desc_error_list.parse_node(errors_node, source)
    #print(errors)

    states_node = btl_parsing.find_tree_section(root, 'states', source, raise_error = False)
    states = btl_parser_desc_state_list.parse_node(states_node, source)
    #print(states)

    start_commands_node = btl_parsing.find_tree_section(root, 'start_commands', source, raise_error = False)
    start_commands = btl_parser_desc_state_command_list.parse_node(start_commands_node, source)

    end_commands_node = btl_parsing.find_tree_section(root, 'end_commands', source, raise_error = False)
    end_commands = btl_parser_desc_state_command_list.parse_node(end_commands_node, source)
    
    return btl_parser_desc(header,
                           errors,
                           states,
                           start_commands,
                           end_commands,
                           source_text = text)

  @classmethod
  def parse_file(clazz, filename):
    filename = file_check.check_file(filename)
    text = file_util.read(filename, codec = 'utf-8')
    return clazz.parse_text(text, source = filename)

  def generate_code(self, buf, namespace, name):
    check.check_btl_code_gen_buffer(buf)
    check.check_string(namespace)
    check.check_string(name)

    buf.write_line(f'''
#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

from bes.system.check import check
from bes.btl.btl_parser_base import btl_parser_base
from bes.btl.btl_parser_runtime_error import btl_parser_runtime_error
from bes.btl.btl_parser_state_base import btl_parser_state_base
''')

    buf.write_line(f'class {namespace}_{name}(btl_parser_base):')
    buf.write_linesep()
    with buf.indent_pusher(depth = 1) as _:
      self.errors.generate_code(buf)
      buf.write_linesep()
      self.states.generate_code(buf, self.errors)

    buf.write_lines(f'''
  def __init__(self, lexer):
    check.check_btl_lexer(lexer)
''')
    with buf.indent_pusher(depth = 2) as _:
      buf.write_line('states = {')
      with buf.indent_pusher() as _42:
        for state in self.states:
          state_class_name = f'_state_{state.name}'
          buf.write_line(f'\'{state.name}\': self.{state_class_name}(self, lexer.log_tag),')
      buf.write_line('}')
      buf.write_lines(f'super().__init__(lexer, self._DESC_TEXT, states)')

    with buf.indent_pusher(depth = 1) as _:
      buf.write_lines(f'''
def do_start_commands(self, context):
  self.log_d(f'do_start_commands:')

def do_end_commands(self, context):
  self.log_d(f'do_start_commands:')
''')
      
    with buf.indent_pusher(depth = 1) as _:
      desc_text = self.source_text or ''
      buf.write_line(f'_DESC_TEXT = """')
    buf.write_line(f'{self.source_text}')
    buf.write_line(f'"""')
    buf.write_line(f'check.register_class({namespace}_{name}, include_seq = False)')
      
  def write_code(self, output_filename, namespace, name, indent_width = 2):
    check.check_string(output_filename)
    check.check_string(namespace)
    check.check_string(name)
    check.check_int(indent_width)

    buf = btl_code_gen_buffer(indent_width = indent_width)
    self.generate_code(buf, namespace, name)
    file_util.save(output_filename, content = buf.get_value())

check.register_class(btl_parser_desc, include_seq = False)
