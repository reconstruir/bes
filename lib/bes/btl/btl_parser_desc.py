#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

import os

from collections import namedtuple

from ..common.json_util import json_util
from ..fs.file_check import file_check
from ..fs.file_util import file_util
from ..system.check import check
from ..text.tree_text_parser import tree_text_parser
from ..version.semantic_version import semantic_version

from .btl_code_gen_buffer import btl_code_gen_buffer
from .btl_desc_text_node import btl_desc_text_node
from .btl_error import btl_error
from .btl_parser_desc_error_list import btl_parser_desc_error_list
from .btl_parser_desc_header import btl_parser_desc_header
from .btl_parser_desc_mermaid import btl_parser_desc_mermaid
from .btl_parser_desc_state_command_list import btl_parser_desc_state_command_list
from .btl_parser_desc_state_list import btl_parser_desc_state_list

class btl_parser_desc(namedtuple('btl_parser_desc', 'header, errors, states, start_commands, end_commands, desc_text, desc_source')):
  
  def __new__(clazz,
              header,
              errors,
              states,
              start_commands,
              end_commands,
              desc_text,
              desc_source):
    header = check.check_btl_parser_desc_header(header)
    errors = check.check_btl_parser_desc_error_list(errors)
    states = check.check_btl_parser_desc_state_list(states)
    start_commands = check.check_btl_parser_desc_state_command_list(start_commands)
    end_commands = check.check_btl_parser_desc_state_command_list(end_commands)
    check.check_string(desc_text)
    check.check_string(desc_source)

    return clazz.__bases__[0].__new__(clazz,
                                      header,
                                      errors,
                                      states,
                                      start_commands,
                                      end_commands,
                                      desc_text,
                                      desc_source)

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
  def parse_text(clazz, desc_text, desc_source):
    check.check_string(desc_text)
    check.check_string(desc_source)

    root = tree_text_parser.parse(desc_text,
                                  strip_comments = True,
                                  root_name = 'btl_parser_desc',
                                  node_class = btl_desc_text_node)

    parser_node = root.find_tree_section('parser', desc_source)
    header = btl_parser_desc_header.parse_node(parser_node, desc_source)
    #print(header)

    errors_node = root.find_tree_section('errors', desc_source, raise_error = False)
    errors = btl_parser_desc_error_list.parse_node(errors_node, desc_source)
    #print(errors)

    states_node = root.find_tree_section('states', desc_source, raise_error = False)
    states = btl_parser_desc_state_list.parse_node(states_node, desc_source)
    #print(states)

    start_commands_node = root.find_tree_section('start_commands', desc_source, raise_error = False)
    start_commands = btl_parser_desc_state_command_list.parse_node(start_commands_node, desc_source)

    end_commands_node = root.find_tree_section('end_commands', desc_source, raise_error = False)
    end_commands = btl_parser_desc_state_command_list.parse_node(end_commands_node, desc_source)
    
    return btl_parser_desc(header,
                           errors,
                           states,
                           start_commands,
                           end_commands,
                           desc_text,
                           desc_source)

  @classmethod
  def parse_file(clazz, filename):
    filename = file_check.check_file(filename)
    text = file_util.read(filename, codec = 'utf-8')
    return clazz.parse_text(text, os.path.basename(filename))

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
    
    log_tag = f'{namespace}_{name}'
''')
    with buf.indent_pusher(depth = 2) as _:
      buf.write_line('states = {')
      with buf.indent_pusher() as _42:
        for state in self.states:
          state_class_name = f'_state_{state.name}'
          buf.write_line(f'\'{state.name}\': self.{state_class_name}(self, log_tag),')
      buf.write_line('}')
      buf.write_lines(f'super().__init__(log_tag, lexer, states)')

    with buf.indent_pusher(depth = 1) as _:
      buf.write_lines(f'''
def do_start_commands(self, context):
  self.log_d(f'do_start_commands:')
''')
      with buf.indent_pusher(depth = 1) as _1:
        self.start_commands.generate_code(buf, self.errors)

      buf.write_lines(f'''
def do_end_commands(self, context):
  self.log_d(f'do_start_commands:')
''')
      with buf.indent_pusher(depth = 1) as _1:
        self.end_commands.generate_code(buf, self.errors)

    with buf.indent_pusher(depth = 1) as _:
      buf.write_lines(f'''
@classmethod
#@abstractmethod
def desc_source(clazz):
  return '{self.desc_source}'

@classmethod
#@abstractmethod
def desc_text(clazz):
''')
    with buf.indent_pusher(depth = 2) as _:
      buf.write_line(f'return """\\')
    buf.write_line(f'{self.desc_text}')
    buf.write_line(f'"""')
#    with buf.indent_pusher(depth = 1) as _:
#      desc_text = self.desc_text or ''
#      buf.write_line(f'_DESC_TEXT = """')
#    buf.write_line(f'{self.desc_text}')
#    buf.write_line(f'"""')
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
